"""Testes REST reais com o test_client do Flask."""
import tempfile
import unittest

try:
    from servidor.app import create_app
except ImportError:  # testes de regras ainda podem rodar sem Flask
    create_app = None


@unittest.skipIf(create_app is None, "Instale Flask para executar testes HTTP.")
class TesteAPI(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.cliente = create_app(self.temp.name).test_client()

    def tearDown(self):
        self.temp.cleanup()

    def test_fluxo_completo(self):
        c = self.cliente
        self.assertEqual(c.get("/saude").json["status"], "ok")
        aluno = c.post("/alunos", json={"nome": "Ana", "matricula": "100"})
        self.assertEqual(aluno.status_code, 201)
        self.assertEqual(c.get("/alunos").json[0]["nome"], "Ana")
        atividade = c.post("/atividades", json={"titulo": "Trabalho", "descricao": "P1", "valor_maximo": 10})
        self.assertEqual(atividade.status_code, 201)
        nota = c.post("/notas", json={"aluno_id": 1, "atividade_id": 1, "valor": 8.5})
        self.assertEqual(nota.status_code, 201)
        self.assertEqual(c.get("/alunos/1/media").json["media"], 8.5)
        self.assertEqual(len(c.get("/alunos/1/notas").json), 1)
        self.assertEqual(c.put("/notas/1", json={"valor": 9}).json["valor"], 9)
        self.assertEqual(c.get("/alunos/1/media").json["media"], 9)
        self.assertEqual(c.delete("/alunos/1").status_code, 200)
        self.assertEqual(c.get("/notas").json, [])

    def test_respostas_de_erro(self):
        c = self.cliente
        self.assertEqual(c.post("/alunos", json={"nome": "", "matricula": "1"}).status_code, 400)
        self.assertEqual(c.post("/alunos", data="texto", content_type="text/plain").status_code, 400)
        self.assertEqual(c.get("/alunos/999").status_code, 404)
        self.assertEqual(c.post("/alunos", json={"nome": "Ana", "matricula": "1"}).status_code, 201)
        self.assertEqual(c.post("/alunos", json={"nome": "Bia", "matricula": "1"}).status_code, 409)
        self.assertEqual(c.post("/notas", json={"aluno_id": 1, "atividade_id": 999, "valor": 7}).status_code, 404)


if __name__ == "__main__":
    unittest.main()
