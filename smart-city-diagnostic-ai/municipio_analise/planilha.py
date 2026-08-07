from __future__ import annotations

import pandas as pd

from .config import Config
from .utils import normalizar_coluna


def carregar_planilha(config: Config) -> pd.DataFrame:
    config.validar(exigir_planilha=True, exigir_api=False)
    df = pd.read_excel(config.caminho_planilha)
    df.columns = [normalizar_coluna(c) for c in df.columns]
    if config.coluna_municipio not in df.columns:
        raise KeyError(f"Coluna obrigatória ausente: {config.coluna_municipio}")
    if config.coluna_populacao not in df.columns:
        raise KeyError(f"Coluna obrigatória ausente: {config.coluna_populacao}")
    return df


def listar_municipios(df: pd.DataFrame, coluna_municipio: str) -> list[str]:
    return df[coluna_municipio].dropna().astype(str).unique().tolist()


def obter_linha_municipio(df: pd.DataFrame, coluna_municipio: str, municipio: str):
    linhas = df[df[coluna_municipio].astype(str) == str(municipio)]
    if linhas.empty:
        raise ValueError(f"Município não encontrado na planilha: {municipio}")
    return linhas.iloc[0]
