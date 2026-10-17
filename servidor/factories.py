"""Fábricas dos objetos de domínio (Padrão Factory Method).

O serviço conhece apenas o contrato da fábrica. Isso desacopla a criação
dos registros de modelo das regras de negócio do serviço e permite criar
classes customizadas para testes ou extensões.
"""
from abc import ABC, abstractmethod

from servidor.models import Aluno, Atividade, Nota


class FabricaRegistros(ABC):
    """Creator do Factory Method usado pelo serviço."""

    @abstractmethod
    def criar_aluno(self, registro):
        raise NotImplementedError

    @abstractmethod
    def criar_atividade(self, registro):
        raise NotImplementedError

    @abstractmethod
    def criar_nota(self, registro):
        raise NotImplementedError

    def criar(self, tipo, registro):
        """Factory Method genérico parametrizado por tipo."""
        tipos = {
            "aluno": self.criar_aluno,
            "atividade": self.criar_atividade,
            "nota": self.criar_nota,
        }
        tipo_normalizado = str(tipo).strip().lower()
        if tipo_normalizado not in tipos:
            raise ValueError(f"Tipo de registro desconhecido: {tipo}")
        return tipos[tipo_normalizado](registro)


class FabricaRegistrosPadrao(FabricaRegistros):
    """Factory Method concreto para os três tipos do domínio."""

    def criar_aluno(self, registro):
        return Aluno(**registro)

    def criar_atividade(self, registro):
        return Atividade(**registro)

    def criar_nota(self, registro):
        return Nota(**registro)
