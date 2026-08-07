"""Classificação de porte municipal e de indicadores em dimensão/tópico."""
from __future__ import annotations

import json
import unicodedata
from importlib import resources

from .data.dimensoes import DIMENSOES, PALAVRAS_CHAVE_TOPICO
from .exceptions import ClassificacaoError
from .models import IndicadorClassificado


def normalizar(texto) -> str:
    """Remove acentos e caixa para facilitar comparação de palavras-chave."""
    texto = unicodedata.normalize("NFKD", str(texto))
    return texto.encode("ascii", errors="ignore").decode("utf-8").lower()


class ClassificadorIndicadores:
    """Classifica indicadores em dimensão/tópico/chunk.

    Ordem de resolução:
    1) correspondência exata no mapa;
    2) fallback por palavras-chave;
    3) fallback semântico por embeddings/FAISS, quando um índice é fornecido;
    4) registro em ``nao_classificados``.
    """

    LIMITE_PEQUENO_PORTE = 50_000
    LIMITE_MEDIO_PORTE = 300_000
    LIMIAR_RELEVANCIA_TOPICO = 0.75

    def __init__(
        self,
        mapa_indicadores: dict[str, IndicadorClassificado],
        colunas_nao_indicadores: set[str],
        indice_topicos=None,
    ):
        self._mapa_indicadores = mapa_indicadores
        self._colunas_nao_indicadores = colunas_nao_indicadores
        self._indice_topicos = indice_topicos
        self.nao_classificados: list[str] = []

    @classmethod
    def carregar_padrao(cls, indice_topicos=None) -> "ClassificadorIndicadores":
        try:
            mapa_raw = json.loads(
                resources.files("municipio_analise.data").joinpath("indicadores_map.json").read_text(encoding="utf-8")
            )
            colunas_raw = json.loads(
                resources.files("municipio_analise.data")
                .joinpath("colunas_nao_indicadores.json")
                .read_text(encoding="utf-8")
            )
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            raise ClassificacaoError(f"Falha ao carregar dados de classificação: {exc}") from exc

        mapa = {
            normalizar(nome): IndicadorClassificado(
                dimensao=dados["dimensao"], topico=dados["topico"], chunk_id=dados["chunk_id"]
            )
            for nome, dados in mapa_raw.items()
        }
        colunas = {normalizar(c) for c in colunas_raw}
        return cls(
            mapa_indicadores=mapa,
            colunas_nao_indicadores=colunas,
            indice_topicos=indice_topicos,
        )

    @staticmethod
    def classificar_porte(populacao: float) -> str:
        if populacao <= ClassificadorIndicadores.LIMITE_PEQUENO_PORTE:
            return "pequeno porte"
        if populacao <= ClassificadorIndicadores.LIMITE_MEDIO_PORTE:
            return "médio porte"
        return "grande porte"

    def classificar_indicador_por_embedding(self, nome_indicador: str) -> IndicadorClassificado | None:
        """Retorna o tópico semanticamente mais próximo, se superar o limiar."""
        if self._indice_topicos is None:
            return None
        resultados = self._indice_topicos.similarity_search_with_relevance_scores(nome_indicador, k=1)
        if not resultados:
            return None
        doc, score = resultados[0]
        if score < self.LIMIAR_RELEVANCIA_TOPICO:
            return None
        return IndicadorClassificado(
            dimensao=doc.metadata["dimensao"],
            topico=doc.metadata["topico"],
            chunk_id=doc.metadata["chunk_id"],
        )

    def classificar_indicador(self, nome_indicador: str) -> IndicadorClassificado | None:
        if normalizar(nome_indicador) in self._colunas_nao_indicadores:
            return None

        nome_norm = normalizar(nome_indicador)
        if nome_norm in self._mapa_indicadores:
            return self._mapa_indicadores[nome_norm]

        melhor, melhor_score = None, 0
        for dimensao, info in DIMENSOES.items():
            for topico in info["topicos"]:
                palavras = PALAVRAS_CHAVE_TOPICO.get(topico, [])
                score = sum(1 for p in palavras if normalizar(p) in nome_norm)
                if score > melhor_score:
                    melhor_score = score
                    melhor = IndicadorClassificado(
                        dimensao=dimensao,
                        topico=topico.replace("_", " ").title(),
                        chunk_id=f"{info['prefixo']}_{topico}",
                    )

        if melhor:
            return melhor

        classificacao_embedding = self.classificar_indicador_por_embedding(nome_indicador)
        if classificacao_embedding:
            return classificacao_embedding

        self.nao_classificados.append(nome_indicador)
        return None

    def classificar_todos(self, indicadores: dict[str, object]) -> dict[str, dict[str, object]]:
        por_dimensao: dict[str, dict[str, object]] = {d: {} for d in DIMENSOES}
        for nome, valor in indicadores.items():
            classificacao = self.classificar_indicador(nome)
            if classificacao:
                por_dimensao[classificacao.dimensao][nome] = valor
        return por_dimensao
