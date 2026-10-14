"""Teste da Facade com servidor HTTP falso local (sem bibliotecas externas)."""
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

from cliente.api_client import APIClient, ErroAPI


class ServidorFalso(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        if self.path == "/saude":
            conteudo = {"aplicacao": "gerenciador_notas", "status": "ok"}
            status = 200
        elif self.path == "/alunos":
            conteudo = [{"id": 1, "nome": "Ana", "matricula": "100"}]
            status = 200
        else:
            conteudo = {"erro": "Não encontrado"}
            status = 404
        resposta = json.dumps(conteudo).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(resposta)))
        self.end_headers()
        self.wfile.write(resposta)


class TesteFacade(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servidor = HTTPServer(("127.0.0.1", 0), ServidorFalso)
        cls.thread = threading.Thread(target=cls.servidor.serve_forever, daemon=True)
        cls.thread.start()
        cls.api = APIClient(f"http://127.0.0.1:{cls.servidor.server_port}")

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()
        cls.thread.join(timeout=3)

    def test_conexao_e_listagem(self):
        self.assertTrue(self.api.verificar_conexao())
        self.assertEqual(self.api.listar_alunos()[0]["nome"], "Ana")

    def test_http_erro_com_mensagem(self):
        with self.assertRaisesRegex(ErroAPI, "Não encontrado"):
            self.api.notas_do_aluno(999)


if __name__ == "__main__":
    unittest.main()
