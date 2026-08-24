from __future__ import annotations

import json
from pathlib import Path

from .utils import normalizar_coluna

_DATA_DIR = Path(__file__).with_name("data")


def _carregar_json(nome: str):
    return json.loads((_DATA_DIR / nome).read_text(encoding="utf-8"))


CHUNKS_CARTA = _carregar_json("carta_chunks.json")
TOPICOS_SEM_CHUNK_NA_CARTA = set(_carregar_json("topicos_sem_chunk_na_carta.json"))

_MAPA_INDICADORES_BRUTO = _carregar_json("mapa_indicadores.json")
MAPA_INDICADORES = {normalizar_coluna(k): v for k, v in _MAPA_INDICADORES_BRUTO.items()}

_MAPA_NIVEL_MATURIDADE_BRUTO = _carregar_json("mapa_nivel_maturidade.json")
MAPA_NIVEL_MATURIDADE = {
    normalizar_coluna(k): normalizar_coluna(v)
    for k, v in _MAPA_NIVEL_MATURIDADE_BRUTO.items()
}

COLUNAS_NAO_INDICADORES = {
    normalizar_coluna(c) for c in _carregar_json("colunas_nao_indicadores.json")
}

_DADOS_CONTEXTUAIS_BRUTO = _carregar_json("dados_contextuais.json")
DADOS_CONTEXTUAIS_MAPA = {
    normalizar_coluna(coluna): {"dimensao": dimensao, "rotulo": coluna}
    for coluna, dimensao in _DADOS_CONTEXTUAIS_BRUTO.items()
}

CARTA_REVISADA_SNAPSHOT = _carregar_json("carta_revisada_snapshot.json")
