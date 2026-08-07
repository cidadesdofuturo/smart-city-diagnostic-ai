from __future__ import annotations

import pandas as pd

from .dados import DADOS_CONTEXTUAIS_MAPA
from .taxonomia import DIMENSOES


def obter_dados_contextuais(dimensao: str, linha_planilha) -> dict:
    dados = {}
    for chave_normalizada, info in DADOS_CONTEXTUAIS_MAPA.items():
        if info["dimensao"] != dimensao:
            continue
        if chave_normalizada in linha_planilha.index:
            valor = linha_planilha[chave_normalizada]
            if not pd.isna(valor):
                dados[info["rotulo"]] = valor
    return dados


def obter_todos_dados_contextuais(linha_planilha) -> dict:
    dados = {}
    for dimensao in DIMENSOES:
        dados.update(obter_dados_contextuais(dimensao, linha_planilha))
    return dados
