"""Regras de negócio; independente do Flask e da interface Qt."""
from dataclasses import asdict
from math import isfinite
from threading import RLock

from servidor.factories import FabricaRegistros, FabricaRegistrosPadrao
from servidor.repository import RepositorioJSON
from servidor.strategies import EstrategiaMedia, MediaNormalizada


class ErroNegocio(Exception):
    def __init__(self, mensagem, status=400):
        super().__init__(mensagem)
        self.status = status


def texto_obrigatorio(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise ErroNegocio(f"{campo} é obrigatório.")
    return valor.strip()


def matricula_valida(valor):
    """Matrícula acadêmica: texto numérico, mantendo zeros à esquerda."""
    matricula = texto_obrigatorio(valor, "Matrícula")
    if not matricula.isdecimal():
        raise ErroNegocio("Matrícula deve conter apenas números.")
    return matricula


def numero_positivo(valor, campo):
    # bool é subtipo de int em Python; não deve ser aceito como número.
    if isinstance(valor, bool):
        raise ErroNegocio(f"{campo} deve ser um número positivo.")
    try:
        numero = float(valor)
    except (TypeError, ValueError, OverflowError):
        raise ErroNegocio(f"{campo} deve ser um número positivo.") from None
    if not isfinite(numero) or numero <= 0:
        raise ErroNegocio(f"{campo} deve ser um número positivo.")
    return numero


def numero_nao_negativo(valor, campo):
    if isinstance(valor, bool):
        raise ErroNegocio(f"{campo} deve ser um número válido.")
    try:
        numero = float(valor)
    except (TypeError, ValueError, OverflowError):
        raise ErroNegocio(f"{campo} deve ser um número válido.") from None
    if not isfinite(numero) or numero < 0:
        raise ErroNegocio(f"{campo} deve ser um número maior ou igual a zero.")
    return numero


def id_valido(valor, campo):
    # IDs vêm de JSON ou URL e podem ser inteiros ou strings de dígitos.
    if isinstance(valor, bool) or not (isinstance(valor, int) or (isinstance(valor, str) and valor.isdecimal())):
        raise ErroNegocio(f"{campo} inválido.")
    numero = int(valor)
    if numero <= 0:
        raise ErroNegocio(f"{campo} inválido.")
    return numero


class GerenciadorService:
    """Facade estrutural do domínio e Contexto comportamental do Strategy.

    Reúne e orquestra as operações de alunos, atividades (avaliações), notas e
    boletins, ocultando a complexidade dos múltiplos repositórios JSON, da
    fábrica de criação de registros (Factory Method) e da estratégia de cálculo
    (Strategy).
    """

    def __init__(self, diretorio_dados, fabrica=None, estrategia_media=None):
        pasta = diretorio_dados
        self.alunos = RepositorioJSON(pasta / "alunos.json")
        self.atividades = RepositorioJSON(pasta / "atividades.json")
        self.notas = RepositorioJSON(pasta / "notas.json")
        self.fabrica = fabrica or FabricaRegistrosPadrao()
        self.estrategia_media = estrategia_media or MediaNormalizada()
        if not isinstance(self.fabrica, FabricaRegistros):
            raise TypeError("fabrica deve implementar FabricaRegistros")
        if not isinstance(self.estrategia_media, EstrategiaMedia):
            raise TypeError("estrategia_media deve implementar EstrategiaMedia")
        self._lock = RLock()  # mantém as operações relacionadas coordenadas

    def definir_estrategia_media(self, estrategia):
        """Contexto do padrão Strategy: permite trocar a estratégia dinamicamente."""
        from servidor.strategies import obter_estrategia
        estrategia_instancia = obter_estrategia(estrategia)
        if not isinstance(estrategia_instancia, EstrategiaMedia):
            raise TypeError("estrategia deve implementar EstrategiaMedia")
        self.estrategia_media = estrategia_instancia
        return self.estrategia_media

    def listar_alunos(self):
        return self.alunos.listar()

    def consultar_aluno(self, codigo):
        aluno = self.alunos.buscar(codigo)
        if aluno is None:
            raise ErroNegocio("Aluno não encontrado.", 404)
        return aluno

    def criar_aluno(self, dados):
        nome = texto_obrigatorio(dados.get("nome"), "Nome")
        matricula = matricula_valida(dados.get("matricula"))
        with self._lock:
            if any(a["matricula"] == matricula for a in self.alunos.listar()):
                raise ErroNegocio("Matrícula já cadastrada.", 409)
            registro = self.alunos.adicionar({"nome": nome, "matricula": matricula})
            return asdict(self.fabrica.criar_aluno(registro))

    def editar_aluno(self, codigo, dados):
        nome = texto_obrigatorio(dados.get("nome"), "Nome")
        matricula = matricula_valida(dados.get("matricula"))
        with self._lock:
            self.consultar_aluno(codigo)
            if any(a["id"] != codigo and a["matricula"] == matricula for a in self.alunos.listar()):
                raise ErroNegocio("Matrícula já cadastrada.", 409)
            return self.alunos.atualizar(codigo, {"nome": nome, "matricula": matricula})

    def excluir_aluno(self, codigo):
        with self._lock:
            self.consultar_aluno(codigo)
            self.notas.excluir_se(lambda nota: nota["aluno_id"] == codigo)
            self.alunos.excluir(codigo)
            return {"mensagem": "Aluno e suas notas excluídos."}

    def listar_atividades(self):
        return self.atividades.listar()

    def consultar_atividade(self, codigo):
        atividade = self.atividades.buscar(codigo)
        if atividade is None:
            raise ErroNegocio("Atividade não encontrada.", 404)
        return atividade

    def criar_atividade(self, dados):
        titulo = texto_obrigatorio(dados.get("titulo"), "Título")
        descricao = dados.get("descricao", "")
        if not isinstance(descricao, str):
            raise ErroNegocio("Descrição inválida.")
        maximo = numero_positivo(dados.get("valor_maximo"), "Valor máximo")
        registro = self.atividades.adicionar({
            "titulo": titulo, "descricao": descricao.strip(), "valor_maximo": maximo
        })
        return asdict(self.fabrica.criar_atividade(registro))

    def editar_atividade(self, codigo, dados):
        titulo = texto_obrigatorio(dados.get("titulo"), "Título")
        descricao = dados.get("descricao", "")
        if not isinstance(descricao, str):
            raise ErroNegocio("Descrição inválida.")
        maximo = numero_positivo(dados.get("valor_maximo"), "Valor máximo")
        with self._lock:
            self.consultar_atividade(codigo)
            # Não permite diminuir a nota máxima abaixo de notas já atribuídas.
            if any(n["atividade_id"] == codigo and n["valor"] > maximo for n in self.notas.listar()):
                raise ErroNegocio("Há notas maiores que o novo valor máximo.")
            return self.atividades.atualizar(codigo, {
                "titulo": titulo, "descricao": descricao.strip(), "valor_maximo": maximo
            })

    def excluir_atividade(self, codigo):
        with self._lock:
            self.consultar_atividade(codigo)
            self.notas.excluir_se(lambda nota: nota["atividade_id"] == codigo)
            self.atividades.excluir(codigo)
            return {"mensagem": "Atividade e suas notas excluídas."}

    def listar_notas(self):
        return self.notas.listar()

    def consultar_nota(self, codigo):
        nota = self.notas.buscar(codigo)
        if nota is None:
            raise ErroNegocio("Nota não encontrada.", 404)
        return nota

    def validar_nota(self, aluno_id, atividade_id, valor):
        self.consultar_aluno(aluno_id)
        atividade = self.consultar_atividade(atividade_id)
        numero = numero_nao_negativo(valor, "Nota")
        if numero > atividade["valor_maximo"]:
            raise ErroNegocio(f"Nota não pode superar {atividade['valor_maximo']:g}.")
        return numero

    def criar_nota(self, dados):
        aluno_id = id_valido(dados.get("aluno_id"), "Aluno")
        atividade_id = id_valido(dados.get("atividade_id"), "Atividade")
        with self._lock:
            valor = self.validar_nota(aluno_id, atividade_id, dados.get("valor"))
            if any(n["aluno_id"] == aluno_id and n["atividade_id"] == atividade_id for n in self.notas.listar()):
                raise ErroNegocio("Aluno já possui nota nessa atividade. Use atualizar nota.", 409)
            registro = self.notas.adicionar({
                "aluno_id": aluno_id, "atividade_id": atividade_id, "valor": valor
            })
            return asdict(self.fabrica.criar_nota(registro))

    def editar_nota(self, codigo, dados):
        with self._lock:
            existente = self.consultar_nota(codigo)
            # Atualização altera só o valor; evita duplicações por troca de associação.
            valor = self.validar_nota(existente["aluno_id"], existente["atividade_id"], dados.get("valor"))
            return self.notas.atualizar(codigo, {"valor": valor})

    def excluir_nota(self, codigo):
        with self._lock:
            self.consultar_nota(codigo)
            self.notas.excluir(codigo)
            return {"mensagem": "Nota excluída."}

    def notas_do_aluno(self, aluno_id):
        with self._lock:
            self.consultar_aluno(aluno_id)
            atividades = {a["id"]: a for a in self.atividades.listar()}
            retorno = []
            for nota in self.notas.listar():
                if nota["aluno_id"] == aluno_id:
                    atividade = atividades[nota["atividade_id"]]
                    retorno.append({
                        **nota, "atividade": atividade["titulo"],
                        "valor_maximo": atividade["valor_maximo"],
                        "nota_normalizada": round(nota["valor"] / atividade["valor_maximo"] * 10, 2)
                    })
            return retorno

    def media_do_aluno(self, aluno_id, estrategia=None):
        notas = self.notas_do_aluno(aluno_id)
        if estrategia:
            from servidor.strategies import obter_estrategia
            estrategia_usada = obter_estrategia(estrategia)
        else:
            estrategia_usada = self.estrategia_media
        media = estrategia_usada.calcular(notas)
        return {
            "aluno_id": aluno_id,
            "media": media,
            "quantidade_notas": len(notas),
            "escala": getattr(estrategia_usada, "escala", "0 a 10"),
            "criterio": getattr(estrategia_usada, "nome", "Normalizada"),
            "criterio_codigo": getattr(estrategia_usada, "codigo", "normalizada"),
        }
