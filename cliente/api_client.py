"""Facade: tela e controlador chamam funções simples, sem lidar com HTTP."""
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ErroAPI(Exception):
    pass


class APIClient:
    def __init__(self, endereco="http://127.0.0.1:8765", timeout=4):
        self.endereco = endereco.rstrip("/")
        self.timeout = timeout

    def _requisitar(self, metodo, caminho, dados=None):
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8") if dados is not None else None
        requisicao = Request(
            self.endereco + caminho,
            data=corpo, method=metodo,
            headers={"Content-Type": "application/json", "Accept": "application/json"}
        )
        try:
            with urlopen(requisicao, timeout=self.timeout) as resposta:
                return json.loads(resposta.read().decode("utf-8"))
        except HTTPError as erro:
            try:
                resposta = json.loads(erro.read().decode("utf-8"))
                mensagem = resposta.get("erro", str(erro))
            except (ValueError, UnicodeDecodeError, AttributeError):
                mensagem = f"Erro HTTP {erro.code}"
            raise ErroAPI(mensagem) from erro
        except (URLError, TimeoutError, OSError) as erro:
            raise ErroAPI("Não foi possível comunicar com o servidor local. "
                          "Verifique se ele está aberto.") from erro
        except (ValueError, UnicodeDecodeError) as erro:
            raise ErroAPI("O servidor respondeu com dados inválidos.") from erro

    def verificar_conexao(self):
        resposta = self._requisitar("GET", "/saude")
        return resposta.get("aplicacao") == "gerenciador_notas" and resposta.get("status") == "ok"

    def listar_alunos(self):
        return self._requisitar("GET", "/alunos")

    def criar_aluno(self, nome, matricula):
        return self._requisitar("POST", "/alunos", {"nome": nome, "matricula": matricula})

    def editar_aluno(self, codigo, nome, matricula):
        return self._requisitar("PUT", f"/alunos/{codigo}", {"nome": nome, "matricula": matricula})

    def excluir_aluno(self, codigo):
        return self._requisitar("DELETE", f"/alunos/{codigo}")

    def listar_atividades(self):
        return self._requisitar("GET", "/atividades")

    def criar_atividade(self, titulo, descricao, valor_maximo):
        return self._requisitar("POST", "/atividades", {
            "titulo": titulo, "descricao": descricao, "valor_maximo": valor_maximo
        })

    def editar_atividade(self, codigo, titulo, descricao, valor_maximo):
        return self._requisitar("PUT", f"/atividades/{codigo}", {
            "titulo": titulo, "descricao": descricao, "valor_maximo": valor_maximo
        })

    def excluir_atividade(self, codigo):
        return self._requisitar("DELETE", f"/atividades/{codigo}")

    def listar_notas(self):
        return self._requisitar("GET", "/notas")

    def criar_nota(self, aluno_id, atividade_id, valor):
        return self._requisitar("POST", "/notas", {
            "aluno_id": aluno_id, "atividade_id": atividade_id, "valor": valor
        })

    def editar_nota(self, codigo, valor):
        return self._requisitar("PUT", f"/notas/{codigo}", {"valor": valor})

    def excluir_nota(self, codigo):
        return self._requisitar("DELETE", f"/notas/{codigo}")

    def notas_do_aluno(self, aluno_id):
        return self._requisitar("GET", f"/alunos/{aluno_id}/notas")

    def media_do_aluno(self, aluno_id):
        return self._requisitar("GET", f"/alunos/{aluno_id}/media")
