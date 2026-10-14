"""Regras de negócio; independente do Flask e da interface Qt."""
from dataclasses import asdict
from math import isfinite
from threading import RLock

from servidor.models import Aluno, Atividade, Nota
from servidor.repository import RepositorioJSON


class ErroNegocio(Exception):
    def __init__(self, mensagem, status=400):
        super().__init__(mensagem)
        self.status = status


def texto_obrigatorio(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise ErroNegocio(f"{campo} é obrigatório.")
    return valor.strip()


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
    def __init__(self, diretorio_dados):
        pasta = diretorio_dados
        self.alunos = RepositorioJSON(pasta / "alunos.json")
        self.atividades = RepositorioJSON(pasta / "atividades.json")
        self.notas = RepositorioJSON(pasta / "notas.json")
        self._lock = RLock()  # mantém as operações relacionadas coordenadas

    def listar_alunos(self):
        return self.alunos.listar()

    def consultar_aluno(self, codigo):
        aluno = self.alunos.buscar(codigo)
        if aluno is None:
            raise ErroNegocio("Aluno não encontrado.", 404)
        return aluno

    def criar_aluno(self, dados):
        nome = texto_obrigatorio(dados.get("nome"), "Nome")
        matricula = texto_obrigatorio(dados.get("matricula"), "Matrícula")
        with self._lock:
            if any(a["matricula"] == matricula for a in self.alunos.listar()):
                raise ErroNegocio("Matrícula já cadastrada.", 409)
            registro = self.alunos.adicionar({"nome": nome, "matricula": matricula})
            return asdict(Aluno(**registro))

    def editar_aluno(self, codigo, dados):
        nome = texto_obrigatorio(dados.get("nome"), "Nome")
        matricula = texto_obrigatorio(dados.get("matricula"), "Matrícula")
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
        return asdict(Atividade(**self.atividades.adicionar({
            "titulo": titulo, "descricao": descricao.strip(), "valor_maximo": maximo
        })))

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
            return asdict(Nota(**self.notas.adicionar({
                "aluno_id": aluno_id, "atividade_id": atividade_id, "valor": valor
            })))

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

    def media_do_aluno(self, aluno_id):
        notas = self.notas_do_aluno(aluno_id)
        # Cada nota é proporcionalmente convertida para escala 0..10.
        # Atividades não avaliadas não entram na média.
        media = round(sum(n["valor"] / n["valor_maximo"] * 10 for n in notas) / len(notas), 2) if notas else None
        return {"aluno_id": aluno_id, "media": media, "quantidade_notas": len(notas), "escala": "0 a 10"}
