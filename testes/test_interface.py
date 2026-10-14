"""Teste de comportamento Qt: executa em modo offscreen quando PySide6 está disponível."""
import os
import unittest

if os.name != "nt":
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtWidgets import QApplication
    from cliente.controlador import Controlador
    from cliente.janela import JanelaPrincipal
except ImportError:
    QApplication = None


class ClienteSimulado:
    """A interface fala com uma Facade simulada, nunca com JSON diretamente."""
    def __init__(self):
        self.alunos = []

    def listar_alunos(self):
        return list(self.alunos)

    def listar_atividades(self):
        return []

    def listar_notas(self):
        return []

    def criar_aluno(self, nome, matricula):
        aluno = {"id": len(self.alunos) + 1, "nome": nome, "matricula": matricula}
        self.alunos.append(aluno)
        return aluno


@unittest.skipIf(QApplication is None, "Instale PySide6 para executar testes de interface Qt.")
class TesteInterface(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_botao_cadastrar_chama_facade_e_atualiza_tabela(self):
        api = ClienteSimulado()
        janela = JanelaPrincipal()
        _controlador = Controlador(janela, api)
        janela.aluno_nome.setText("Ana")
        janela.aluno_matricula.setText("2026001")
        janela.btn_aluno_criar.click()
        self.assertEqual(api.alunos[0]["nome"], "Ana")
        self.assertEqual(janela.tabela_alunos.rowCount(), 1)
        self.assertEqual(janela.tabela_alunos.item(0, 2).text(), "2026001")
        janela.close()


if __name__ == "__main__":
    unittest.main()
