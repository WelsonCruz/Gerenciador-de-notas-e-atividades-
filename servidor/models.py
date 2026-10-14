"""Model (domínio): dados que o sistema manipula."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Aluno:
    id: int
    nome: str
    matricula: str


@dataclass(frozen=True)
class Atividade:
    id: int
    titulo: str
    descricao: str
    valor_maximo: float


@dataclass(frozen=True)
class Nota:
    id: int
    aluno_id: int
    atividade_id: int
    valor: float
