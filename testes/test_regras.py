"""Testes de unidade das regras de negócio: não exigem Qt nem Flask."""
import json
import tempfile
import unittest
from pathlib import Path

from servidor.repository import ErroRepositorio
from servidor.services import ErroNegocio, GerenciadorService


class TesteRegras(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.pasta = Path(self.temp.name)
        self.servico = GerenciadorService(self.pasta)

    def tearDown(self):
        self.temp.cleanup()

    def aluno(self, matricula="100"):
        return self.servico.criar_aluno({"nome": "Ana", "matricula": matricula})

    def atividade(self, maximo=10):
        return self.servico.criar_atividade({"titulo": "Prova", "descricao": "Avaliação", "valor_maximo": maximo})

    def test_cadastrar_listar_editar_excluir_aluno(self):
        aluno = self.aluno()
        self.assertEqual(aluno["id"], 1)
        self.assertEqual(len(self.servico.listar_alunos()), 1)
        self.servico.editar_aluno(1, {"nome": "Ana Maria", "matricula": "101"})
        self.assertEqual(self.servico.consultar_aluno(1)["nome"], "Ana Maria")
        self.servico.excluir_aluno(1)
        self.assertEqual(self.servico.listar_alunos(), [])

    def test_matricula_duplicada(self):
        self.aluno()
        with self.assertRaises(ErroNegocio) as contexto:
            self.aluno()
        self.assertEqual(contexto.exception.status, 409)

    def test_matricula_duplicada_na_edicao(self):
        self.aluno("100")
        self.aluno("200")
        with self.assertRaises(ErroNegocio) as contexto:
            self.servico.editar_aluno(2, {"nome": "Bia", "matricula": "100"})
        self.assertEqual(contexto.exception.status, 409)

    def test_nome_e_titulo_obrigatorios(self):
        with self.assertRaises(ErroNegocio):
            self.servico.criar_aluno({"nome": " ", "matricula": "101"})
        with self.assertRaises(ErroNegocio):
            self.servico.criar_atividade({"titulo": "", "valor_maximo": 10})

    def test_nota_fora_da_faixa_e_referencias_invalidas(self):
        aluno = self.aluno()
        atividade = self.atividade(10)
        with self.assertRaises(ErroNegocio):
            self.servico.criar_nota({"aluno_id": aluno["id"], "atividade_id": atividade["id"], "valor": 11})
        with self.assertRaises(ErroNegocio):
            self.servico.criar_nota({"aluno_id": 999, "atividade_id": atividade["id"], "valor": 5})
        with self.assertRaises(ErroNegocio):
            self.servico.criar_nota({"aluno_id": aluno["id"], "atividade_id": 999, "valor": 5})
        with self.assertRaises(ErroNegocio):
            self.servico.criar_nota({"aluno_id": aluno["id"], "atividade_id": atividade["id"], "valor": -1})

    def test_uma_nota_por_atividade_e_atualizacao(self):
        a = self.aluno()
        t = self.atividade()
        nota = self.servico.criar_nota({"aluno_id": a["id"], "atividade_id": t["id"], "valor": 7})
        with self.assertRaises(ErroNegocio) as contexto:
            self.servico.criar_nota({"aluno_id": a["id"], "atividade_id": t["id"], "valor": 8})
        self.assertEqual(contexto.exception.status, 409)
        atualizada = self.servico.editar_nota(nota["id"], {"valor": 9})
        self.assertEqual(atualizada["valor"], 9)
        self.servico.excluir_nota(nota["id"])
        self.assertEqual(self.servico.listar_notas(), [])

    def test_media_em_escala_dez_e_nao_avaliadas(self):
        a = self.aluno()
        t1 = self.atividade(10)
        t2 = self.servico.criar_atividade({"titulo": "Projeto", "valor_maximo": 5})
        self.servico.criar_atividade({"titulo": "Sem nota", "valor_maximo": 10})
        self.assertIsNone(self.servico.media_do_aluno(a["id"])["media"])
        self.servico.criar_nota({"aluno_id": a["id"], "atividade_id": t1["id"], "valor": 8})
        self.servico.criar_nota({"aluno_id": a["id"], "atividade_id": t2["id"], "valor": 3})
        self.assertEqual(self.servico.media_do_aluno(a["id"])["media"], 7)
        self.assertEqual(self.servico.media_do_aluno(a["id"])["quantidade_notas"], 2)

    def test_exclusao_em_cascata(self):
        a = self.aluno()
        t = self.atividade()
        self.servico.criar_nota({"aluno_id": a["id"], "atividade_id": t["id"], "valor": 7})
        self.servico.excluir_atividade(t["id"])
        self.assertEqual(self.servico.listar_notas(), [])
        t = self.atividade()
        self.servico.criar_nota({"aluno_id": a["id"], "atividade_id": t["id"], "valor": 8})
        self.servico.excluir_aluno(a["id"])
        self.assertEqual(self.servico.listar_notas(), [])

    def test_persistencia_em_json(self):
        self.aluno()
        novo_servico = GerenciadorService(self.pasta)
        self.assertEqual(novo_servico.listar_alunos()[0]["matricula"], "100")
        with (self.pasta / "alunos.json").open(encoding="utf-8") as arquivo:
            self.assertEqual(json.load(arquivo)[0]["nome"], "Ana")

    def test_json_corrompido_gera_erro_sem_apagar(self):
        caminho = self.pasta / "alunos.json"
        caminho.write_text("texto inválido", encoding="utf-8")
        with self.assertRaises(ErroRepositorio):
            self.servico.listar_alunos()
        self.assertEqual(caminho.read_text(encoding="utf-8"), "texto inválido")

    def test_numeros_invalidos(self):
        a = self.aluno()
        t = self.atividade()
        for valor in (True, float("nan"), float("inf"), "nan", "texto"):
            with self.subTest(valor=valor):
                with self.assertRaises(ErroNegocio):
                    self.servico.criar_nota({"aluno_id": a["id"], "atividade_id": t["id"], "valor": valor})

    def test_atividade_nao_pode_ter_maximo_abaixo_de_nota_existente(self):
        a = self.aluno()
        t = self.atividade(10)
        self.servico.criar_nota({"aluno_id": a["id"], "atividade_id": t["id"], "valor": 9})
        with self.assertRaises(ErroNegocio):
            self.servico.editar_atividade(t["id"], {"titulo": "Prova", "descricao": "", "valor_maximo": 8})


if __name__ == "__main__":
    unittest.main()
