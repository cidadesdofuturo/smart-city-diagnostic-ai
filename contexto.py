"""Dados contextuais municipais usados apenas para enriquecer a análise textual.

Esses campos (PIB, IDH-M, GINI, CAPAG, estrutura de TI, instituições de
pesquisa etc.) permanecem fora do conjunto de indicadores da metodologia e
não entram no cálculo de maturidade, na priorização nem geram sugestões por si.
"""
from __future__ import annotations

import json
from importlib import resources

import pandas as pd

from .classificador import normalizar
from .exceptions import ClassificacaoError


class DadosContextuaisRepository:
    """Carrega o mapa campo contextual -> dimensão e extrai valores da planilha."""

    def __init__(self, mapa: dict[str, dict[str, str]]):
        self._mapa = mapa

    @classmethod
    def carregar_padrao(cls) -> "DadosContextuaisRepository":
        try:
            bruto = json.loads(
                resources.files("municipio_analise.data")
                .joinpath("dados_contextuais_map.json")
                .read_text(encoding="utf-8")
            )
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            raise ClassificacaoError(f"Falha ao carregar dados contextuais: {exc}") from exc

        mapa = {
            normalizar(rotulo): {"dimensao": dimensao, "rotulo": rotulo}
            for rotulo, dimensao in bruto.items()
        }
        return cls(mapa)

    def obter_por_dimensao(self, dimensao: str, linha_planilha: pd.Series) -> dict[str, object]:
        dados: dict[str, object] = {}
        for chave_normalizada, info in self._mapa.items():
            if info["dimensao"] != dimensao or chave_normalizada not in linha_planilha.index:
                continue
            valor = linha_planilha[chave_normalizada]
            if not pd.isna(valor):
                dados[info["rotulo"]] = valor
        return dados

    def obter_todos(self, dimensoes, linha_planilha: pd.Series) -> dict[str, object]:
        dados: dict[str, object] = {}
        for dimensao in dimensoes:
            dados.update(self.obter_por_dimensao(dimensao, linha_planilha))
        return dados
