from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .dados import COLUNAS_NAO_INDICADORES, MAPA_INDICADORES
from .taxonomia import DIMENSOES, PALAVRAS_CHAVE_TOPICO
from .utils import normalizar_coluna, normalizar_texto


class ClassificadorIndicadores:
    """Classifica colunas da planilha por dimensão/tópico.

    Mantém a API do pacote modular anterior: o primeiro argumento pode ser
    um ``fallback_semantico`` callable. Para a arquitetura nova, também aceita
    diretamente o serviço de embeddings, desde que exponha
    ``classificar_topico(nome_indicador)``.
    """

    def __init__(
        self,
        fallback_semantico: Callable[[str], dict[str, Any] | None] | Any | None = None,
    ):
        self.embeddings = None
        self.fallback_semantico: Callable[[str], dict[str, Any] | None] | None = None

        if callable(fallback_semantico):
            self.fallback_semantico = fallback_semantico
        elif fallback_semantico is not None and hasattr(fallback_semantico, "classificar_topico"):
            self.embeddings = fallback_semantico
            self.fallback_semantico = fallback_semantico.classificar_topico

        # Nome histórico preservado para não quebrar consumidores/testes.
        self.nao_classificados: list[str] = []

    @property
    def indicadores_nao_classificados(self) -> list[str]:
        """Alias usado pelo pipeline sincronizado com o notebook."""
        return self.nao_classificados

    def limpar_nao_classificados(self) -> None:
        self.nao_classificados.clear()

    def classificar(self, nome_indicador: str):
        nome_col = normalizar_coluna(nome_indicador)
        if nome_col in COLUNAS_NAO_INDICADORES:
            return None
        if nome_col in MAPA_INDICADORES:
            return MAPA_INDICADORES[nome_col]

        nome_norm = normalizar_texto(nome_indicador)
        melhor, melhor_score = None, 0
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
            try:
                classificacao = self.fallback_semantico(nome_indicador)
            except Exception:
                classificacao = None
            if classificacao:
                return classificacao

        # A versão modular anterior registrava a chave normalizada. Preservar
        # esse comportamento facilita auditoria e evita regressões nos testes.
        self.nao_classificados.append(nome_col)
        return None


# Alias curto para compatibilidade com versões anteriores.
Classificador = ClassificadorIndicadores
