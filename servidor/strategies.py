"""Estratégias substituíveis para cálculo de médias (Padrão Strategy).

Permite que o algoritmo de cálculo de média varie independentemente dos
clientes que o utilizam. O GerenciadorService atua como a classe de contexto,
podendo trocar a estratégia em tempo de execução ou por parâmetro de consulta.
"""
from abc import ABC, abstractmethod


class EstrategiaMedia(ABC):
    """Contrato abstrato do padrão Strategy para cálculo de médias."""

    codigo = "abstrata"
    nome = "Estratégia base"
    descricao = "Contrato de cálculo de médias"
    escala = "0 a 10"

    @abstractmethod
    def calcular(self, notas):
        """Calcula e retorna a média das notas ou None se a lista for vazia."""
        raise NotImplementedError


class MediaNormalizada(EstrategiaMedia):
    """Média aritmética das notas convertidas proporcionalmente para 0 a 10.

    Cada atividade tem peso igual após normalização, independentemente
    da nota máxima original.
    Exemplo: 8/10 (80%) e 4/5 (80%) resultam em média 8.00/10.
    """

    codigo = "normalizada"
    nome = "Normalizada (0 a 10 - padrão)"
    descricao = "Média aritmética com notas convertidas para escala 0 a 10"
    escala = "0 a 10"

    def calcular(self, notas):
        if not notas:
            return None
        valores = [nota["valor"] / nota["valor_maximo"] * 10 for nota in notas]
        return round(sum(valores) / len(valores), 2)


class MediaPonderadaPorValorMaximo(EstrategiaMedia):
    """Média ponderada na qual a nota máxima de cada atividade atua como peso.

    Atividades de maior valor têm impacto proporcionalmente maior no resultado.
    Exemplo: 5/5 (peso 5) e 5/10 (peso 10) resultam em (5+5)/(5+10)*10 = 6.67/10.
    """

    codigo = "ponderada"
    nome = "Ponderada pelo valor máximo"
    descricao = "O valor máximo de cada atividade atua como peso na composição final"
    escala = "0 a 10"

    def calcular(self, notas):
        if not notas:
            return None
        total_obtido = sum(nota["valor"] for nota in notas)
        total_maximo = sum(nota["valor_maximo"] for nota in notas)
        if total_maximo <= 0:
            return 0.0
        return round((total_obtido / total_maximo) * 10, 2)


class MediaAritmeticaDireta(EstrategiaMedia):
    """Média aritmética dos valores brutos obtidos, sem normalização percentual."""

    codigo = "direta"
    nome = "Aritmética direta dos pontos"
    descricao = "Média direta dos pontos brutos obtidos pelo aluno"
    escala = "Pontos brutos"

    def calcular(self, notas):
        if not notas:
            return None
        return round(sum(nota["valor"] for nota in notas) / len(notas), 2)


ESTRATEGIAS_DISPONIVEIS = {
    "normalizada": MediaNormalizada,
    "ponderada": MediaPonderadaPorValorMaximo,
    "direta": MediaAritmeticaDireta,
}


def obter_estrategia(identificador_ou_instancia):
    """Retorna uma instância de EstrategiaMedia a partir de nome ou instância."""
    if isinstance(identificador_ou_instancia, EstrategiaMedia):
        return identificador_ou_instancia
    if isinstance(identificador_ou_instancia, str):
        chave = identificador_ou_instancia.strip().lower()
        if chave in ESTRATEGIAS_DISPONIVEIS:
            return ESTRATEGIAS_DISPONIVEIS[chave]()
        raise ValueError(
            f"Critério de média '{identificador_ou_instancia}' desconhecido. "
            f"Opções disponíveis: {', '.join(ESTRATEGIAS_DISPONIVEIS.keys())}"
        )
    return MediaNormalizada()
