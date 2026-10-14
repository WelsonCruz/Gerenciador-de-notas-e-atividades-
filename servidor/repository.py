"""Repository: leitura/gravação de JSON sem depender do Flask ou da interface.

Um arquivo guarda uma lista de dicionários, com IDs inteiros. A substituição
atômica evita arquivos parciais se a gravação falhar durante a escrita.
"""
import json
import os
import tempfile
from pathlib import Path
from threading import RLock


class ErroRepositorio(Exception):
    """Dados locais não puderam ser lidos ou gravados."""


class RepositorioJSON:
    def __init__(self, caminho):
        self.caminho = Path(caminho)
        self._lock = RLock()
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        if not self.caminho.exists():
            self._gravar([])

    def _ler(self):
        try:
            with self.caminho.open("r", encoding="utf-8") as arquivo:
                registros = json.load(arquivo)
            if not isinstance(registros, list) or any(
                not isinstance(r, dict) or type(r.get("id")) is not int for r in registros
            ):
                raise ValueError("Lista de registros com IDs inteiros esperada")
            return registros
        except (OSError, ValueError, TypeError) as erro:
            raise ErroRepositorio(f"Não foi possível ler {self.caminho.name}: {erro}") from erro

    def _gravar(self, registros):
        temporario = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.caminho.parent,
                prefix=f".{self.caminho.stem}-", suffix=".tmp", delete=False
            ) as arquivo:
                temporario = arquivo.name
                json.dump(registros, arquivo, ensure_ascii=False, indent=2)
                arquivo.write("\n")
            os.replace(temporario, self.caminho)
        except OSError as erro:
            raise ErroRepositorio(f"Não foi possível salvar {self.caminho.name}: {erro}") from erro
        finally:
            if temporario and os.path.exists(temporario):
                os.unlink(temporario)

    def listar(self):
        with self._lock:
            return self._ler()

    def buscar(self, codigo):
        with self._lock:
            return next((r for r in self._ler() if r["id"] == codigo), None)

    def adicionar(self, dados):
        with self._lock:
            registros = self._ler()
            codigo = max((r["id"] for r in registros), default=0) + 1
            registro = {"id": codigo, **dados}
            registros.append(registro)
            self._gravar(registros)
            return registro

    def atualizar(self, codigo, dados):
        with self._lock:
            registros = self._ler()
            for i, registro in enumerate(registros):
                if registro["id"] == codigo:
                    registros[i] = {**registro, **dados, "id": codigo}
                    self._gravar(registros)
                    return registros[i]
            return None

    def excluir(self, codigo):
        with self._lock:
            registros = self._ler()
            restantes = [r for r in registros if r["id"] != codigo]
            if len(restantes) == len(registros):
                return False
            self._gravar(restantes)
            return True

    def excluir_se(self, predicado):
        """Remove registros associados após exclusão de aluno/atividade."""
        with self._lock:
            registros = self._ler()
            restantes = [r for r in registros if not predicado(r)]
            if len(restantes) != len(registros):
                self._gravar(restantes)
            return len(registros) - len(restantes)
