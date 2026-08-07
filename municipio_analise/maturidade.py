"""Nível de maturidade e seleção de chunks da Carta por dimensão."""
from __future__ import annotations

import json
import math
from importlib import resources
from typing import Optional

import pandas as pd

from .carta import CartaRepository
from .classificador import ClassificadorIndicadores, normalizar
from .data.dimensoes import CHUNKS_GERAIS, NIVEIS_TEXTUAIS
from .exceptions import ClassificacaoError
from .models import ChunkCarta


class GestorMaturidade:
    """Prioriza tópicos de menor maturidade e seleciona base conceitual.

    Quando um tópico não possui chunk dedicado na Carta, pode usar um índice
    FAISS para recuperar o chunk semanticamente mais próximo dentro da mesma
    dimensão, replicando o fallback do notebook de referência.
    """

    def __init__(
        self,
        carta: CartaRepository,
        classificador: ClassificadorIndicadores,
        mapa_nivel_maturidade: dict[str, str],
        indice_chunks=None,
    ):
        self._carta = carta
        self._classificador = classificador
        self._mapa_nivel_maturidade = mapa_nivel_maturidade
        self._indice_chunks = indice_chunks

    @classmethod
    def carregar_padrao(
        cls,
        carta: CartaRepository,
        classificador: ClassificadorIndicadores,
        indice_chunks=None,
    ) -> "GestorMaturidade":
        try:
            mapa_raw = json.loads(
                resources.files("municipio_analise.data")
                .joinpath("nivel_maturidade_map.json")
                .read_text(encoding="utf-8")
            )
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            raise ClassificacaoError(f"Falha ao carregar mapa de nível de maturidade: {exc}") from exc

        mapa = {normalizar(k): normalizar(v) for k, v in mapa_raw.items()}
        return cls(
            carta=carta,
            classificador=classificador,
            mapa_nivel_maturidade=mapa,
            indice_chunks=indice_chunks,
        )

    def estimar_nivel_por_valor(self, valor) -> Optional[float]:
        if valor is None or (isinstance(valor, float) and math.isnan(valor)):
            return None
        if isinstance(valor, (int, float)):
            return float(valor)
        return NIVEIS_TEXTUAIS.get(normalizar(valor))

    def obter_nivel(
        self,
        nome_indicador: str,
        valor,
        linha_planilha: "pd.Series | None" = None,
    ) -> Optional[float]:
        nm_col = self._mapa_nivel_maturidade.get(normalizar(nome_indicador))
        if nm_col is not None and linha_planilha is not None and nm_col in linha_planilha.index:
            nivel_real = linha_planilha[nm_col]
            if not pd.isna(nivel_real):
                try:
                    return float(nivel_real)
                except (TypeError, ValueError):
                    pass
        return self.estimar_nivel_por_valor(valor)

    def selecionar_chunks_dimensao(
        self,
        dimensao: str,
        indicadores_dimensao: dict[str, object],
        linha_planilha: "pd.Series | None" = None,
        usar_fallback_semantico: bool = True,
    ) -> list[ChunkCarta]:
        chunks_gerais = self._carta.chunks_gerais(CHUNKS_GERAIS)

        pior_nivel_por_chunk: dict[str, float] = {}
        for nome, valor in indicadores_dimensao.items():
            classificacao = self._classificador.classificar_indicador(nome)
            if not classificacao or classificacao.dimensao != dimensao:
                continue
            nivel = self.obter_nivel(nome, valor, linha_planilha)
            nivel_efetivo = 99.0 if nivel is None else nivel
            pior_nivel_por_chunk[classificacao.chunk_id] = min(
                pior_nivel_por_chunk.get(classificacao.chunk_id, 99.0), nivel_efetivo
            )

        topicos_ordenados = sorted(pior_nivel_por_chunk, key=lambda cid: pior_nivel_por_chunk[cid])

        chunks_topicos: list[ChunkCarta] = []
        chunk_ids_incluidos: set[str] = set()
        for cid in topicos_ordenados:
            if cid in self._carta:
                chunks_topicos.append(self._carta.obter(cid))
                chunk_ids_incluidos.add(cid)
                continue

            if (
                usar_fallback_semantico
                and self._indice_chunks is not None
                and cid in self._carta.topicos_sem_chunk
            ):
                nome_topico = cid.split("_", 1)[1].replace("_", " ")
                resultados = self._indice_chunks.similarity_search(
                    nome_topico,
                    k=1,
                    filter={"dimensao": dimensao},
                    fetch_k=50,
                )
                for doc in resultados:
                    chunk_id_encontrado = doc.metadata["chunk_id"]
                    if chunk_id_encontrado in chunk_ids_incluidos:
                        continue
                    chunk = self._carta.obter_opcional(chunk_id_encontrado)
                    if chunk is not None:
                        chunks_topicos.append(chunk)
                        chunk_ids_incluidos.add(chunk_id_encontrado)

        return chunks_gerais + chunks_topicos
