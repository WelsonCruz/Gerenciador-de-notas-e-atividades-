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

    def notas_do_aluno(self, aluno_id):
        return [
            {"atividade": "Prova", "valor": 10, "valor_maximo": 10, "nota_normalizada": 10},
            {"atividade": "Trabalho", "valor": 8.5, "valor_maximo": 10, "nota_normalizada": 8.5},
        ]

    def media_do_aluno(self, aluno_id, criterio=None):
        if criterio == "direta":
            return {
                "media": 9.25,
                "quantidade_notas": 2,
                "criterio": "Aritmética direta dos pontos",
                "escala": "Pontos brutos",
            }
        return {"media": 9.25, "quantidade_notas": 2, "criterio": "Normalizada", "escala": "0 a 10"}

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
        self.assertEqual(janela.card_alunos.valor.text(), "0")
        janela.aluno_nome.setText("Ana")
        janela.aluno_matricula.setText("2026001")
        janela.btn_aluno_criar.click()
        self.assertEqual(api.alunos[0]["nome"], "Ana")
        self.assertEqual(janela.tabela_alunos.rowCount(), 1)
        self.assertEqual(janela.tabela_alunos.item(0, 2).text(), "2026001")
        self.assertEqual(janela.card_alunos.valor.text(), "1")
        janela.close()

    def test_consulta_exibe_media_das_duas_notas(self):
        api = ClienteSimulado()
        api.alunos.append({"id": 1, "nome": "Ana", "matricula": "100"})
        janela = JanelaPrincipal()
        _controlador = Controlador(janela, api)
        janela.consulta_aluno.setCurrentIndex(0)
        janela.btn_consultar.click()
        self.assertEqual(janela.label_media.text(), "Média final: 9.25 / 10")
        self.assertEqual(janela.label_quantidade.text(), "2 nota(s) considerada(s) no cálculo")
        self.assertEqual(janela.tabela_consulta.rowCount(), 2)
        janela.close()

if __name__ == "__main__":
    unittest.main()
