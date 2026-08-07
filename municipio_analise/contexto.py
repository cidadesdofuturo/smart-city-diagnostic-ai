"""Dados contextuais do notebook, separados dos indicadores da metodologia."""
from __future__ import annotations

import pandas as pd

from .utils import normalizar

_DADOS_CONTEXTUAIS_BRUTO = {
    "PIB per capita do município": "Econômica",
    "PIB Agropecuária": "Econômica",
    "PIB Indústria": "Econômica",
    "PIB Serviços": "Econômica",
    "PIB Adminstração Pública": "Econômica",
    "População ocupada com vínculo formal": "Econômica",
    "Capacidade de pagamento dos municípios (CAPAG)": "Econômica",
    "Empregos em TIC": "Econômica",
    "Empresas de TICs no municipio": "Econômica",
    "Número de Empresas em Parques Tecnológicos": "Econômica",
    "Número de Incubadoras credenciadas - Lei de TIC": "Econômica",
    "Número de Instituições de Ensino e Pesquisa em PD&I - Lei de TIC": "Econômica",
    "Número de Centros e/ou Institutos de PD&I - Lei de TIC": "Econômica",
    "Número de Empresas habilitadas - Lei de TIC": "Econômica",
    "Número de empresas - Lei do Bem PD&I": "Econômica",
    "Índice de desenvolvimento humano do município (IDH-M)": "Sociocultural",
    "Índice de GINI da renda domiciliar per capita": "Sociocultural",
    "Número de Campus de Institutos e Universidades Federais": "Sociocultural",
    "Equipe de TI - Tamanho": "Capacidades Institucionais",
    "Estrutura Organizacional de TIC": "Capacidades Institucionais",
    "Incorporação de TICs - Áreas Prioritárias": "Capacidades Institucionais",
    "Governança Tecnológica - Responsáveis": "Capacidades Institucionais",
    "Governança de TI - Responsável": "Capacidades Institucionais",
}

DADOS_CONTEXTUAIS_MAPA = {
    normalizar(coluna): {"dimensao": dimensao, "rotulo": coluna}
    for coluna, dimensao in _DADOS_CONTEXTUAIS_BRUTO.items()
}


def obter_dados_contextuais(dimensao, linha_planilha):
    dados = {}
    for chave_normalizada, info in DADOS_CONTEXTUAIS_MAPA.items():
        if info["dimensao"] != dimensao:
            continue
        if chave_normalizada in linha_planilha.index:
            valor = linha_planilha[chave_normalizada]
            if not pd.isna(valor):
                dados[info["rotulo"]] = valor
    return dados


def obter_todos_dados_contextuais(linha_planilha, dimensoes):
    dados = {}
    for dimensao in dimensoes:
        dados.update(obter_dados_contextuais(dimensao, linha_planilha))
    return dados
