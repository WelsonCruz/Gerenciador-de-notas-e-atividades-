"""API REST local com Flask. Rotas delegam regras ao Service."""
import os
import sys
from pathlib import Path

# Permite 'python servidor/app.py' e importação como pacote.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flask import Flask, jsonify, request
from servidor.repository import ErroRepositorio
from servidor.services import ErroNegocio, GerenciadorService


def pasta_dados_padrao():
    """Ao empacotar, usa pasta 'dados' junto ao .exe, fora do executável."""
    configurada = os.environ.get("GERENCIADOR_DADOS")
    if configurada:
        return Path(configurada).expanduser().resolve()
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "dados"
    return Path(__file__).resolve().parent / "dados"


def create_app(diretorio_dados=None):
    app = Flask(__name__)
    service = GerenciadorService(Path(diretorio_dados) if diretorio_dados else pasta_dados_padrao())
    app.config["JSON_AS_ASCII"] = False
    app.config["SERVICE"] = service

    @app.errorhandler(ErroNegocio)
    def erro_de_negocio(erro):
        return jsonify({"erro": str(erro)}), erro.status

    @app.errorhandler(ErroRepositorio)
    def erro_de_arquivo(erro):
        return jsonify({"erro": str(erro)}), 500

    @app.errorhandler(400)
    def requisicao_invalida(_erro):
        return jsonify({"erro": "Requisição inválida: envie JSON válido."}), 400

    @app.errorhandler(404)
    def rota_nao_encontrada(_erro):
        return jsonify({"erro": "Endpoint não encontrado."}), 404

    def corpo():
        dados = request.get_json(silent=True)
        if not isinstance(dados, dict):
            raise ErroNegocio("Envie um objeto JSON válido.")
        return dados

    @app.get("/saude")
    def saude():
        return jsonify({"aplicacao": "gerenciador_notas", "status": "ok"})

    @app.get("/alunos")
    def listar_alunos():
        return jsonify(service.listar_alunos())

    @app.post("/alunos")
    def criar_aluno():
        return jsonify(service.criar_aluno(corpo())), 201

    @app.get("/alunos/<int:codigo>")
    def buscar_aluno(codigo):
        return jsonify(service.consultar_aluno(codigo))

    @app.put("/alunos/<int:codigo>")
    def editar_aluno(codigo):
        return jsonify(service.editar_aluno(codigo, corpo()))

    @app.delete("/alunos/<int:codigo>")
    def excluir_aluno(codigo):
        return jsonify(service.excluir_aluno(codigo))

    @app.get("/atividades")
    def listar_atividades():
        return jsonify(service.listar_atividades())

    @app.post("/atividades")
    def criar_atividade():
        return jsonify(service.criar_atividade(corpo())), 201

    @app.get("/atividades/<int:codigo>")
    def buscar_atividade(codigo):
        return jsonify(service.consultar_atividade(codigo))

    @app.put("/atividades/<int:codigo>")
    def editar_atividade(codigo):
        return jsonify(service.editar_atividade(codigo, corpo()))

    @app.delete("/atividades/<int:codigo>")
    def excluir_atividade(codigo):
        return jsonify(service.excluir_atividade(codigo))

    @app.get("/notas")
    def listar_notas():
        return jsonify(service.listar_notas())

    @app.post("/notas")
    def criar_nota():
        return jsonify(service.criar_nota(corpo())), 201

    @app.get("/notas/<int:codigo>")
    def buscar_nota(codigo):
        return jsonify(service.consultar_nota(codigo))

    @app.put("/notas/<int:codigo>")
    def editar_nota(codigo):
        return jsonify(service.editar_nota(codigo, corpo()))

    @app.delete("/notas/<int:codigo>")
    def excluir_nota(codigo):
        return jsonify(service.excluir_nota(codigo))

    @app.get("/alunos/<int:codigo>/notas")
    def consultar_notas(codigo):
        return jsonify(service.notas_do_aluno(codigo))

    @app.get("/alunos/<int:codigo>/media")
    def consultar_media(codigo):
        criterio = request.args.get("criterio")
        try:
            return jsonify(service.media_do_aluno(codigo, estrategia=criterio))
        except ValueError as erro:
            raise ErroNegocio(str(erro)) from erro

    @app.get("/estrategias-media")
    def listar_estrategias_media():
        from servidor.strategies import ESTRATEGIAS_DISPONIVEIS
        return jsonify([
            {
                "codigo": est.codigo,
                "nome": est.nome,
                "descricao": est.descricao,
                "escala": est.escala,
            }
            for est in (cls() for cls in ESTRATEGIAS_DISPONIVEIS.values())
        ])

    return app


if __name__ == "__main__":
    print("Servidor local: http://127.0.0.1:8765", flush=True)
    create_app().run(host="127.0.0.1", port=8765, debug=False, use_reloader=False, threaded=False)
