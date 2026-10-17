"""Inicia interface Qt e, quando necessário, o servidor Flask local."""
import os
import subprocess
import sys
import time
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QMessageBox
from cliente.api_client import APIClient, ErroAPI
from cliente.controlador import Controlador
from cliente.janela import JanelaPrincipal


def iniciar_servidor_se_necessario(api):
    """Retorna processo de servidor iniciado aqui, ou None se já está ativo.

    O Flask escuta somente em 127.0.0.1. Se a porta for ocupada por outro
    serviço, a aplicação explica o problema em vez de tentar usá-lo.
    """
    try:
        if api.verificar_conexao():
            return None
        raise RuntimeError("A porta 8765 está ocupada por outro serviço.")
    except ErroAPI:
        pass  # Sem servidor: iniciar um novo.

    if getattr(sys, "frozen", False):
        pasta = Path(sys.executable).resolve().parent
        servidor = pasta / ("ServidorNotas.exe" if os.name == "nt" else "ServidorNotas")
        if not servidor.is_file():
            raise RuntimeError("Executável do servidor não encontrado junto ao aplicativo.")
        comando = [str(servidor)]
    else:
        pasta = Path(__file__).resolve().parents[1]
        comando = [sys.executable, str(pasta / "servidor" / "app.py")]

    argumentos = {"cwd": str(pasta), "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if os.name == "nt":
        argumentos["creationflags"] = subprocess.CREATE_NO_WINDOW
    processo = subprocess.Popen(comando, **argumentos)
    # PyInstaller --onefile pode precisar de alguns segundos na primeira abertura.
    limite = time.monotonic() + 20
    while time.monotonic() < limite:
        if processo.poll() is not None:
            raise RuntimeError("O servidor encerrou na inicialização. Verifique as dependências e a porta 8765.")
        try:
            if api.verificar_conexao():
                return processo
        except ErroAPI:
            pass
        time.sleep(0.2)
    processo.terminate()
    raise RuntimeError("O servidor não respondeu no tempo esperado.")


def main():
    app = QApplication(sys.argv)
    # Base consistente entre Windows e outros ambientes; a View aplica os
    # ajustes locais do tema por meio de seletores específicos.
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    app.setApplicationName("Gerenciador de Notas e Atividades")
    api = APIClient(timeout=1)
    processo = None
    try:
        processo = iniciar_servidor_se_necessario(api)
        janela = JanelaPrincipal()
        controlador = Controlador(janela, api)
        # Preserva o controlador pelo tempo de vida da janela.
        janela.controlador = controlador
        janela.show()
        return app.exec()
    except (RuntimeError, OSError, ErroAPI) as erro:
        QMessageBox.critical(None, "Erro ao iniciar o sistema", str(erro))
        return 1
    finally:
        if processo is not None and processo.poll() is None:
            processo.terminate()
            try:
                processo.wait(timeout=3)
            except subprocess.TimeoutExpired:
                processo.kill()


if __name__ == "__main__":
    raise SystemExit(main())
