"""Controller: conecta botões da View aos métodos da Facade (APIClient)."""
from PySide6.QtWidgets import QMessageBox
from cliente.api_client import ErroAPI


class Controlador:
    def __init__(self, janela, api):
        self.janela = janela
        self.api = api
        self.alunos = []
        self.atividades = []
        self.notas = []
        self._ligar_eventos()
        self.atualizar_listagens()

    def _ligar_eventos(self):
        j = self.janela
        j.btn_aluno_criar.clicked.connect(self.criar_aluno)
        j.btn_aluno_editar.clicked.connect(self.editar_aluno)
        j.btn_aluno_excluir.clicked.connect(self.excluir_aluno)
        j.btn_aluno_limpar.clicked.connect(self.limpar_aluno)
        j.tabela_alunos.itemSelectionChanged.connect(self.selecionar_aluno)

        j.btn_atividade_criar.clicked.connect(self.criar_atividade)
        j.btn_atividade_editar.clicked.connect(self.editar_atividade)
        j.btn_atividade_excluir.clicked.connect(self.excluir_atividade)
        j.btn_atividade_limpar.clicked.connect(self.limpar_atividade)
        j.tabela_atividades.itemSelectionChanged.connect(self.selecionar_atividade)

        j.btn_nota_criar.clicked.connect(self.criar_nota)
        j.btn_nota_editar.clicked.connect(self.editar_nota)
        j.btn_nota_excluir.clicked.connect(self.excluir_nota)
        j.nota_atividade.currentIndexChanged.connect(self.atualizar_limite_nota)
        j.tabela_notas.itemSelectionChanged.connect(self.selecionar_nota)
        j.btn_consultar.clicked.connect(self.consultar)

    def executar(self, operacao, mensagem=""):
        try:
            operacao()
            if mensagem:
                self.janela.statusBar().showMessage(mensagem, 5500)
            return True
        except ErroAPI as erro:
            QMessageBox.warning(self.janela, "Não foi possível concluir", str(erro))
            return False

    def confirmar(self, texto):
        return QMessageBox.question(
            self.janela, "Confirmar exclusão", texto,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes

    def exigir_selecao(self, codigo, objeto):
        if codigo is None:
            QMessageBox.information(self.janela, "Selecione um registro", f"Selecione um(a) {objeto} na tabela.")
            return False
        return True

    def atualizar_listagens(self):
        def carregar():
            self.alunos = self.api.listar_alunos()
            self.atividades = self.api.listar_atividades()
            self.notas = self.api.listar_notas()
            j = self.janela
            j.preencher_tabela(j.tabela_alunos, [
                (a["id"], a["nome"], a["matricula"]) for a in self.alunos
            ])
            j.preencher_tabela(j.tabela_atividades, [
                (a["id"], a["titulo"], a["descricao"], f'{a["valor_maximo"]:g}') for a in self.atividades
            ])
            nomes = {a["id"]: a["nome"] for a in self.alunos}
            atividades = {a["id"]: a for a in self.atividades}
            j.preencher_tabela(j.tabela_notas, [
                (n["id"], nomes.get(n["aluno_id"], "—"),
                 atividades.get(n["atividade_id"], {}).get("titulo", "—"),
                 f'{n["valor"]:g}', f'{atividades.get(n["atividade_id"], {}).get("valor_maximo", 0):g}')
                for n in self.notas
            ])
            j.preencher_combo(j.nota_aluno, self.alunos, "nome")
            j.preencher_combo(j.consulta_aluno, self.alunos, "nome")
            j.preencher_combo(j.nota_atividade, self.atividades, "titulo")
            self.atualizar_limite_nota()
        return self.executar(carregar)

    def _depois_de_alterar(self, texto):
        self.atualizar_listagens()
        self.janela.statusBar().showMessage(texto, 5000)

    def limpar_aluno(self):
        j = self.janela
        j.tabela_alunos.clearSelection()
        j.aluno_id_selecionado = None
        j.aluno_nome.clear()
        j.aluno_matricula.clear()

    def selecionar_aluno(self):
        j = self.janela
        linha = j.tabela_alunos.currentRow()
        if linha < 0 or not j.tabela_alunos.selectedItems() or j.tabela_alunos.item(linha, 0) is None:
            return
        codigo = int(j.tabela_alunos.item(linha, 0).text())
        aluno = next((a for a in self.alunos if a["id"] == codigo), None)
        if aluno:
            j.aluno_id_selecionado = codigo
            j.aluno_nome.setText(aluno["nome"])
            j.aluno_matricula.setText(aluno["matricula"])

    def criar_aluno(self):
        j = self.janela
        if self.executar(lambda: self.api.criar_aluno(j.aluno_nome.text(), j.aluno_matricula.text())):
            self.limpar_aluno()
            self._depois_de_alterar("Aluno cadastrado.")

    def editar_aluno(self):
        j = self.janela
        if not self.exigir_selecao(j.aluno_id_selecionado, "aluno"):
            return
        if self.executar(lambda: self.api.editar_aluno(j.aluno_id_selecionado, j.aluno_nome.text(), j.aluno_matricula.text())):
            self.limpar_aluno()
            self._depois_de_alterar("Aluno atualizado.")

    def excluir_aluno(self):
        j = self.janela
        if self.exigir_selecao(j.aluno_id_selecionado, "aluno") and self.confirmar("Excluir aluno e todas as suas notas?"):
            if self.executar(lambda: self.api.excluir_aluno(j.aluno_id_selecionado)):
                self.limpar_aluno()
                self._depois_de_alterar("Aluno excluído.")

    def limpar_atividade(self):
        j = self.janela
        j.tabela_atividades.clearSelection()
        j.atividade_id_selecionada = None
        j.atividade_titulo.clear()
        j.atividade_descricao.clear()
        j.atividade_maximo.setValue(10)

    def selecionar_atividade(self):
        j = self.janela
        linha = j.tabela_atividades.currentRow()
        if linha < 0 or not j.tabela_atividades.selectedItems() or j.tabela_atividades.item(linha, 0) is None:
            return
        codigo = int(j.tabela_atividades.item(linha, 0).text())
        atividade = next((a for a in self.atividades if a["id"] == codigo), None)
        if atividade:
            j.atividade_id_selecionada = codigo
            j.atividade_titulo.setText(atividade["titulo"])
            j.atividade_descricao.setText(atividade["descricao"])
            j.atividade_maximo.setValue(atividade["valor_maximo"])

    def _dados_atividade(self):
        j = self.janela
        return (j.atividade_titulo.text(), j.atividade_descricao.text(), j.atividade_maximo.value())

    def criar_atividade(self):
        if self.executar(lambda: self.api.criar_atividade(*self._dados_atividade())):
            self.limpar_atividade()
            self._depois_de_alterar("Atividade cadastrada.")

    def editar_atividade(self):
        j = self.janela
        if not self.exigir_selecao(j.atividade_id_selecionada, "atividade"):
            return
        if self.executar(lambda: self.api.editar_atividade(j.atividade_id_selecionada, *self._dados_atividade())):
            self.limpar_atividade()
            self._depois_de_alterar("Atividade atualizada.")

    def excluir_atividade(self):
        j = self.janela
        if self.exigir_selecao(j.atividade_id_selecionada, "atividade") and self.confirmar("Excluir atividade e suas notas?"):
            if self.executar(lambda: self.api.excluir_atividade(j.atividade_id_selecionada)):
                self.limpar_atividade()
                self._depois_de_alterar("Atividade excluída.")

    def atualizar_limite_nota(self, *_):
        j = self.janela
        codigo = j.nota_atividade.currentData()
        atividade = next((a for a in self.atividades if a["id"] == codigo), None)
        maximo = atividade["valor_maximo"] if atividade else 10
        j.nota_valor.setMaximum(maximo)

    def selecionar_nota(self):
        j = self.janela
        linha = j.tabela_notas.currentRow()
        if linha < 0 or not j.tabela_notas.selectedItems() or j.tabela_notas.item(linha, 0) is None:
            return
        codigo = int(j.tabela_notas.item(linha, 0).text())
        nota = next((n for n in self.notas if n["id"] == codigo), None)
        if nota:
            j.nota_id_selecionada = codigo
            indice = j.nota_aluno.findData(nota["aluno_id"])
            if indice >= 0:
                j.nota_aluno.setCurrentIndex(indice)
            indice = j.nota_atividade.findData(nota["atividade_id"])
            if indice >= 0:
                j.nota_atividade.setCurrentIndex(indice)
            j.nota_valor.setValue(nota["valor"])

    def criar_nota(self):
        j = self.janela
        if j.nota_aluno.currentData() is None or j.nota_atividade.currentData() is None:
            QMessageBox.information(j, "Dados incompletos", "Cadastre ao menos um aluno e uma atividade.")
            return
        if self.executar(lambda: self.api.criar_nota(
            j.nota_aluno.currentData(), j.nota_atividade.currentData(), j.nota_valor.value()
        )):
            j.nota_id_selecionada = None
            self._depois_de_alterar("Nota registrada.")

    def editar_nota(self):
        j = self.janela
        if not self.exigir_selecao(j.nota_id_selecionada, "nota"):
            return
        if self.executar(lambda: self.api.editar_nota(j.nota_id_selecionada, j.nota_valor.value())):
            j.nota_id_selecionada = None
            self._depois_de_alterar("Nota atualizada.")

    def excluir_nota(self):
        j = self.janela
        if self.exigir_selecao(j.nota_id_selecionada, "nota") and self.confirmar("Excluir esta nota?"):
            if self.executar(lambda: self.api.excluir_nota(j.nota_id_selecionada)):
                j.nota_id_selecionada = None
                self._depois_de_alterar("Nota excluída.")

    def consultar(self):
        j = self.janela
        codigo = j.consulta_aluno.currentData()
        if codigo is None:
            QMessageBox.information(j, "Nenhum aluno", "Cadastre um aluno antes de consultar.")
            return

        def carregar():
            notas = self.api.notas_do_aluno(codigo)
            media = self.api.media_do_aluno(codigo)
            j.preencher_tabela(j.tabela_consulta, [
                (n["atividade"], f'{n["valor"]:g}', f'{n["valor_maximo"]:g}', f'{n["nota_normalizada"]:.2f}')
                for n in notas
            ])
            if media["media"] is None:
                j.label_media.setText("Média: sem notas cadastradas")
            else:
                j.label_media.setText(f'Média: {media["media"]:.2f} / 10  |  {media["quantidade_notas"]} nota(s)')
        self.executar(carregar)
