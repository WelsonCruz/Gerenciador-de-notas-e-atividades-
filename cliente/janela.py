"""View (Qt): monta as telas, não conhece Flask nem arquivos JSON."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDoubleSpinBox, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow, QPushButton, QTabWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
)


class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciador de Notas e Atividades")
        self.resize(940, 640)
        self.aluno_id_selecionado = None
        self.atividade_id_selecionada = None
        self.nota_id_selecionada = None
        abas = QTabWidget()
        abas.addTab(self._aba_alunos(), "Alunos")
        abas.addTab(self._aba_atividades(), "Atividades")
        abas.addTab(self._aba_notas(), "Notas")
        abas.addTab(self._aba_consulta(), "Consulta e média")
        self.setCentralWidget(abas)
        self.statusBar().showMessage("Dados armazenados localmente em JSON | API Flask")
        self.setStyleSheet("""
            QMainWindow { background: #6495ED; }
            QGroupBox { font-weight: 600; margin-top: 10px; padding-top: 10px; }
            QLineEdit, QDoubleSpinBox, QComboBox { min-height: 26px; padding: 3px; }
            QPushButton { min-height: 29px; padding: 3px 12px; }
            QTableWidget { background: black; }
        """)

    @staticmethod
    def _tabela(colunas):
        tabela = QTableWidget(0, len(colunas))
        tabela.setHorizontalHeaderLabels(colunas)
        tabela.horizontalHeader().setStretchLastSection(True)
        tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tabela.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tabela.setAlternatingRowColors(True)
        return tabela

    @staticmethod
    def _botao(texto):
        return QPushButton(texto)

    def _aba_alunos(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        grupo = QGroupBox("Cadastro de alunos")
        formulario = QFormLayout(grupo)
        self.aluno_nome = QLineEdit()
        self.aluno_nome.setPlaceholderText("Ex.: Ana Silva")
        self.aluno_matricula = QLineEdit()
        self.aluno_matricula.setPlaceholderText("Ex.: 2026001")
        formulario.addRow("Nome:", self.aluno_nome)
        formulario.addRow("Matrícula:", self.aluno_matricula)
        layout.addWidget(grupo)
        botoes = QHBoxLayout()
        self.btn_aluno_criar = self._botao("Cadastrar")
        self.btn_aluno_editar = self._botao("Atualizar selecionado")
        self.btn_aluno_excluir = self._botao("Excluir selecionado")
        self.btn_aluno_limpar = self._botao("Limpar campos")
        for botao in (self.btn_aluno_criar, self.btn_aluno_editar, self.btn_aluno_excluir, self.btn_aluno_limpar):
            botoes.addWidget(botao)
        layout.addLayout(botoes)
        layout.addWidget(QLabel("Selecione uma linha para editar ou excluir o aluno."))
        self.tabela_alunos = self._tabela(["ID", "Nome", "Matrícula"])
        layout.addWidget(self.tabela_alunos)
        return pagina

    def _aba_atividades(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        grupo = QGroupBox("Cadastro de atividades")
        formulario = QFormLayout(grupo)
        self.atividade_titulo = QLineEdit()
        self.atividade_titulo.setPlaceholderText("Ex.: Trabalho de Python")
        self.atividade_descricao = QLineEdit()
        self.atividade_descricao.setPlaceholderText("Descrição opcional")
        self.atividade_maximo = QDoubleSpinBox()
        self.atividade_maximo.setDecimals(2)
        self.atividade_maximo.setRange(0.01, 1000000)
        self.atividade_maximo.setValue(10)
        formulario.addRow("Título:", self.atividade_titulo)
        formulario.addRow("Descrição:", self.atividade_descricao)
        formulario.addRow("Nota máxima:", self.atividade_maximo)
        layout.addWidget(grupo)
        botoes = QHBoxLayout()
        self.btn_atividade_criar = self._botao("Cadastrar")
        self.btn_atividade_editar = self._botao("Atualizar selecionada")
        self.btn_atividade_excluir = self._botao("Excluir selecionada")
        self.btn_atividade_limpar = self._botao("Limpar campos")
        for botao in (self.btn_atividade_criar, self.btn_atividade_editar, self.btn_atividade_excluir, self.btn_atividade_limpar):
            botoes.addWidget(botao)
        layout.addLayout(botoes)
        layout.addWidget(QLabel("Excluir uma atividade também exclui as notas ligadas a ela."))
        self.tabela_atividades = self._tabela(["ID", "Título", "Descrição", "Nota máxima"])
        layout.addWidget(self.tabela_atividades)
        return pagina

    def _aba_notas(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        grupo = QGroupBox("Lançamento de notas")
        formulario = QFormLayout(grupo)
        self.nota_aluno = QComboBox()
        self.nota_atividade = QComboBox()
        self.nota_valor = QDoubleSpinBox()
        self.nota_valor.setDecimals(2)
        self.nota_valor.setRange(0, 10)
        formulario.addRow("Aluno:", self.nota_aluno)
        formulario.addRow("Atividade:", self.nota_atividade)
        formulario.addRow("Nota obtida:", self.nota_valor)
        layout.addWidget(grupo)
        botoes = QHBoxLayout()
        self.btn_nota_criar = self._botao("Registrar nota")
        self.btn_nota_editar = self._botao("Atualizar selecionada")
        self.btn_nota_excluir = self._botao("Excluir selecionada")
        for botao in (self.btn_nota_criar, self.btn_nota_editar, self.btn_nota_excluir):
            botoes.addWidget(botao)
        layout.addLayout(botoes)
        layout.addWidget(QLabel("Um aluno pode ter apenas uma nota por atividade. Selecione a nota para alterá-la."))
        self.tabela_notas = self._tabela(["ID", "Aluno", "Atividade", "Nota", "Máxima"])
        layout.addWidget(self.tabela_notas)
        return pagina

    def _aba_consulta(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        cabecalho = QHBoxLayout()
        cabecalho.addWidget(QLabel("Aluno:"))
        self.consulta_aluno = QComboBox()
        cabecalho.addWidget(self.consulta_aluno, 1)
        self.btn_consultar = self._botao("Consultar notas e média")
        cabecalho.addWidget(self.btn_consultar)
        layout.addLayout(cabecalho)
        self.label_media = QLabel("Média: —")
        self.label_media.setStyleSheet("font-size: 20px; font-weight: 700; padding: 12px 4px;")
        layout.addWidget(self.label_media)
        layout.addWidget(QLabel("Média de notas convertidas para a escala de 0 a 10; atividades sem nota são ignoradas."))
        self.tabela_consulta = self._tabela(["Atividade", "Nota obtida", "Máximo", "Equivalente / 10"])
        layout.addWidget(self.tabela_consulta)
        return pagina

    @staticmethod
    def preencher_tabela(tabela, linhas):
        tabela.setRowCount(len(linhas))
        for numero_linha, linha in enumerate(linhas):
            for numero_coluna, valor in enumerate(linha):
                item = QTableWidgetItem(str(valor))
                if numero_coluna == 0:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tabela.setItem(numero_linha, numero_coluna, item)
        tabela.resizeColumnsToContents()

    @staticmethod
    def preencher_combo(combo, opcoes, nome_chave):
        escolha_anterior = combo.currentData()
        combo.blockSignals(True)
        combo.clear()
        for registro in opcoes:
            combo.addItem(registro[nome_chave], registro["id"])
        if escolha_anterior is not None:
            indice = combo.findData(escolha_anterior)
            if indice >= 0:
                combo.setCurrentIndex(indice)
        combo.blockSignals(False)
