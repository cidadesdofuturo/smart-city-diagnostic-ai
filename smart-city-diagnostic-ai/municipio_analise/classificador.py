from __future__ import annotations

from collections.abc import Callable

from .dados import COLUNAS_NAO_INDICADORES, MAPA_INDICADORES
from .taxonomia import DIMENSOES, PALAVRAS_CHAVE_TOPICO
from .utils import normalizar_coluna, normalizar_texto


class ClassificadorIndicadores:
    """Classifica indicadores por mapa explícito, palavras-chave e embeddings."""

    def __init__(self, fallback_semantico: Callable[[str], dict | None] | None = None):
        self.fallback_semantico = fallback_semantico
        self.nao_classificados: list[str] = []

    def limpar_nao_classificados(self) -> None:
        self.nao_classificados.clear()

    def classificar(self, nome_indicador: str) -> dict | None:
        nome_coluna = normalizar_coluna(nome_indicador)

        if nome_coluna in COLUNAS_NAO_INDICADORES:
            return None

        if nome_coluna in MAPA_INDICADORES:
            return MAPA_INDICADORES[nome_coluna]

        nome_norm = normalizar_texto(nome_indicador)
        melhor = None
        melhor_score = 0
        for dimensao, info in DIMENSOES.items():
            for topico in info["topicos"]:
                palavras = PALAVRAS_CHAVE_TOPICO.get(topico, [])
                score = sum(1 for p in palavras if normalizar_texto(p) in nome_norm)
                if score > melhor_score:
                    melhor_score = score
                    melhor = {
                        "dimensao": dimensao,
                        "topico": topico.replace("_", " ").title(),
                        "chunk_id": f"{info['prefixo']}_{topico}",
                    }

        if melhor:
            return melhor

        if self.fallback_semantico is not None:
            classificacao = self.fallback_semantico(nome_indicador)
            if classificacao:
                return classificacao

        self.nao_classificados.append(nome_coluna)
        return None
