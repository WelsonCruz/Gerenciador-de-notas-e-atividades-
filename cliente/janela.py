"""View (Qt): monta as telas, não conhece Flask nem arquivos JSON."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDoubleSpinBox, QFormLayout, QFrame, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow, QPushButton, QTabWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
)


class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciador de Notas e Atividades")
        # Há formulário, ações e tabela em cada aba; esta área evita que a
        # tabela fique comprimida na abertura, sobretudo em Atividades/Notas.
        self.resize(1040, 720)
        self.setMinimumSize(900, 640)
        self.aluno_id_selecionado = None
        self.atividade_id_selecionada = None
        self.nota_id_selecionada = None
        abas = QTabWidget()
        abas.setObjectName("abasPrincipal")
        abas.addTab(self._aba_alunos(), "Alunos")
        abas.addTab(self._aba_atividades(), "Atividades")
        abas.addTab(self._aba_notas(), "Notas")
        abas.addTab(self._aba_consulta(), "Consulta e média")

        cabecalho = QWidget()
        cabecalho.setObjectName("cabecalho")
        cabecalho_layout = QVBoxLayout(cabecalho)
        cabecalho_layout.setContentsMargins(24, 20, 24, 16)
        titulo = QLabel("Gerenciador de notas")
        titulo.setObjectName("tituloAplicacao")
        subtitulo = QLabel("Organize alunos, atividades e resultados em um só lugar")
        subtitulo.setObjectName("subtituloAplicacao")
        cabecalho_layout.addWidget(titulo)
        cabecalho_layout.addWidget(subtitulo)

        principal = QWidget()
        principal.setObjectName("principal")
        principal_layout = QVBoxLayout(principal)
        principal_layout.setContentsMargins(18, 12, 18, 8)
        principal_layout.setSpacing(12)
        principal_layout.addWidget(cabecalho)
        principal_layout.addWidget(self._resumo())
        principal_layout.addWidget(abas, 1)
        self.setCentralWidget(principal)
        self.statusBar().showMessage("Dados armazenados localmente em JSON | API Flask")
        self.setStyleSheet("""
            QMainWindow { background: #eef2f7; }
            QWidget#principal { background: #eef2f7; color: #26364a; }
            #cabecalho {
                background: #173b67;
                border-radius: 12px;
            }
            QLabel#tituloAplicacao {
                color: white;
                font-size: 25px;
                font-weight: 700;
                background: transparent;
            }
            QLabel#subtituloAplicacao {
                color: #cbdcf2;
                font-size: 13px;
                background: transparent;
            }
            QLabel { color: #344b65; background: transparent; }
            QFrame#cardResumo {
                background: white;
                border: 1px solid #d8e1ec;
                border-radius: 10px;
            }
            QLabel#rotuloResumo {
                color: #63758a;
                font-size: 12px;
                font-weight: 600;
            }
            QLabel#valorResumo {
                color: #173b67;
                font-size: 24px;
                font-weight: 700;
            }
            QLabel#indicadorAlunos { color: #1769aa; font-size: 13px; }
            QLabel#indicadorAtividades { color: #16826b; font-size: 13px; }
            QLabel#indicadorNotas { color: #a26716; font-size: 13px; }
            QFrame#painelMedia {
                background: #eaf4fb;
                border: 1px solid #b9d8ed;
                border-radius: 10px;
            }
            QLabel#labelMedia {
                color: #155a89;
                font-size: 24px;
                font-weight: 700;
            }
            QLabel#labelQuantidade {
                color: #52718b;
                font-size: 13px;
            }
            QTabWidget::pane {
                background: white;
                border: 1px solid #d8e1ec;
                border-radius: 10px;
                top: -1px;
            }
            QTabBar::tab {
                background: #e8eef6;
                color: #52657d;
                padding: 11px 20px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                color: #1769aa;
                font-weight: 700;
            }
            QGroupBox {
                background: #ffffff;
                border: 1px solid #d8e1ec;
                border-radius: 9px;
                color: #173b67;
                font-weight: 700;
                margin-top: 12px;
                padding: 16px 12px 10px 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                color: #173b67;
            }
            QLineEdit, QDoubleSpinBox, QComboBox {
                background: #fbfdff;
                color: #1f2937;
                border: 1px solid #c8d5e5;
                border-radius: 6px;
                min-height: 28px;
                padding: 3px 8px;
            }
            QLineEdit:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border: 2px solid #3b82c4;
            }
            QLineEdit::placeholder { color: #8292a6; }
            QComboBox QAbstractItemView {
                background: white;
                color: #1f2937;
                selection-background-color: #d9eaf7;
                selection-color: #173b67;
            }
            QPushButton {
                background: #1769aa;
                color: white;
                border: none;
                border-radius: 6px;
                min-height: 31px;
                padding: 4px 14px;
                font-weight: 600;
            }
            QPushButton:hover { background: #125589; }
            QPushButton:pressed { background: #0d4169; }
            QPushButton#btnSecundario {
                background: #e7edf5;
                color: #344b65;
            }
            QPushButton#btnSecundario:hover { background: #d7e1ed; }
            QPushButton#btnPerigo { background: #c44747; }
            QPushButton#btnPerigo:hover { background: #a93636; }
            QTableWidget {
                background: white;
                alternate-background-color: #f3f7fb;
                border: 1px solid #d8e1ec;
                border-radius: 7px;
                gridline-color: #e5ebf2;
                selection-background-color: #cfe5f7;
                selection-color: #173b67;
            }
            QHeaderView::section {
                background: #eaf1f8;
                color: #344b65;
                border: none;
                border-bottom: 1px solid #d8e1ec;
                padding: 8px;
                font-weight: 700;
            }
            QTableWidget::item { padding: 5px; }
            QTableWidget::item:selected {
                background: #cfe5f7;
                color: #173b67;
            }
            QTableCornerButton::section {
                background: #eaf1f8;
                border: none;
            }
            QScrollBar:vertical {
                background: #f1f5f9;
                width: 10px;
                margin: 2px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #b6c8da;
                min-height: 24px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover { background: #8fa9c0; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            QStatusBar { background: #e7edf5; color: #52657d; }
        """)

    @staticmethod
    def _tabela(colunas):
        tabela = QTableWidget(0, len(colunas))
        tabela.setHorizontalHeaderLabels(colunas)
        # Mantém todas as colunas visíveis e equilibradas. Antes, apenas a
        # última coluna ocupava o espaço livre e os cabeçalhos podiam parecer
        # deslocados ao abrir uma aba ou redimensionar a janela.
        tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tabela.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tabela.setAlternatingRowColors(True)
        tabela.verticalHeader().setVisible(False)
        tabela.setShowGrid(False)
        tabela.setMinimumHeight(220)
        return tabela

    @staticmethod
    def _botao(texto):
        botao = QPushButton(texto)
        if "Excluir" in texto:
            botao.setObjectName("btnPerigo")
        elif "Limpar" in texto:
            botao.setObjectName("btnSecundario")
        return botao

    @staticmethod
    def _cartao_resumo(rotulo, object_name):
        cartao = QFrame()
        cartao.setObjectName("cardResumo")
        layout = QVBoxLayout(cartao)
        layout.setContentsMargins(16, 10, 16, 10)
        indicador = QLabel("●")
        indicador.setObjectName(object_name)
        texto = QLabel(rotulo)
        texto.setObjectName("rotuloResumo")
        valor = QLabel("0")
        valor.setObjectName("valorResumo")
        layout.addWidget(indicador, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(texto)
        layout.addWidget(valor)
        cartao.valor = valor
        return cartao

    def _resumo(self):
        resumo = QWidget()
        layout = QHBoxLayout(resumo)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        self.card_alunos = self._cartao_resumo("Alunos cadastrados", "indicadorAlunos")
        self.card_atividades = self._cartao_resumo("Atividades cadastradas", "indicadorAtividades")
        self.card_notas = self._cartao_resumo("Notas lançadas", "indicadorNotas")
        for card in (self.card_alunos, self.card_atividades, self.card_notas):
            layout.addWidget(card, 1)
        return resumo

    def atualizar_resumo(self, quantidade_alunos, quantidade_atividades, quantidade_notas):
        self.card_alunos.valor.setText(str(quantidade_alunos))
        self.card_atividades.valor.setText(str(quantidade_atividades))
        self.card_notas.valor.setText(str(quantidade_notas))

    def _aba_alunos(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        grupo = QGroupBox("Cadastro de alunos")
        formulario = QFormLayout(grupo)
        self.aluno_nome = QLineEdit()
        self.aluno_nome.setPlaceholderText("Ex.: Seedorf")
        self.aluno_matricula = QLineEdit()
        self.aluno_matricula.setPlaceholderText("Ex.: 676767")
        self.aluno_matricula.setToolTip("Use somente números. Zeros à esquerda são aceitos.")
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
        self.tabela_alunos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
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
        self.tabela_atividades.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
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
        self.tabela_notas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabela_notas)
        return pagina

    def _aba_consulta(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        titulo = QLabel("Boletim do aluno")
        titulo.setStyleSheet("font-size: 18px; font-weight: 700; color: #173b67;")
        layout.addWidget(titulo)
        layout.addWidget(QLabel("Selecione um aluno para visualizar todas as notas e a média final."))
        cabecalho = QHBoxLayout()
        cabecalho.addWidget(QLabel("Aluno:"))
        self.consulta_aluno = QComboBox()
        cabecalho.addWidget(self.consulta_aluno, 1)
        self.btn_consultar = self._botao("Atualizar boletim")
        cabecalho.addWidget(self.btn_consultar)
        layout.addLayout(cabecalho)
        painel_media = QFrame()
        painel_media.setObjectName("painelMedia")
        painel_layout = QVBoxLayout(painel_media)
        painel_layout.setContentsMargins(16, 12, 16, 12)
        self.label_media = QLabel("Média final: —")
        self.label_media.setObjectName("labelMedia")
        self.label_quantidade = QLabel("Nenhuma consulta realizada")
        self.label_quantidade.setObjectName("labelQuantidade")
        painel_layout.addWidget(self.label_media)
        painel_layout.addWidget(self.label_quantidade)
        layout.addWidget(painel_media)
        layout.addWidget(QLabel(
            "A média considera o percentual de cada atividade e converte para 0 a 10. "
            "Ex.: 8,5/10 = 8,5; 8,5/8,5 = 10,0."
        ))
        self.tabela_consulta = self._tabela(["Atividade", "Nota obtida", "Nota máxima", "Equivalente / 10"])
        self.tabela_consulta.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
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
