from __future__ import annotations

import json
from pathlib import Path

from .utils import normalizar_coluna

DATA_DIR = Path(__file__).resolve().parent / "data"


def _ler_json(nome: str):
    return json.loads((DATA_DIR / nome).read_text(encoding="utf-8"))


CHUNKS_CARTA = _ler_json("carta_chunks.json")
MAPA_INDICADORES_BRUTO = _ler_json("mapa_indicadores.json")
MAPA_NIVEL_MATURIDADE_BRUTO = _ler_json("mapa_nivel_maturidade.json")
COLUNAS_NAO_INDICADORES_BRUTO = _ler_json("colunas_nao_indicadores.json")
DADOS_CONTEXTUAIS_BRUTO = _ler_json("dados_contextuais.json")

MAPA_INDICADORES = {
    normalizar_coluna(k): v for k, v in MAPA_INDICADORES_BRUTO.items()
}
MAPA_NIVEL_MATURIDADE = {
    normalizar_coluna(k): normalizar_coluna(v)
    for k, v in MAPA_NIVEL_MATURIDADE_BRUTO.items()
}
COLUNAS_NAO_INDICADORES = {
    normalizar_coluna(c) for c in COLUNAS_NAO_INDICADORES_BRUTO
}
DADOS_CONTEXTUAIS_MAPA = {
    normalizar_coluna(coluna): {"dimensao": dimensao, "rotulo": coluna}
    for coluna, dimensao in DADOS_CONTEXTUAIS_BRUTO.items()
}
