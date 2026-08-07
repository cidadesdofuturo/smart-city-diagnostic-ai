from __future__ import annotations

import pandas as pd

from .dados import MAPA_NIVEL_MATURIDADE
from .utils import normalizar_texto

NIVEIS_TEXTUAIS = {
    "inexistente": 0,
    "nao": 0,
    "não": 0,
    "ausente": 0,
    "inicial": 1,
    "basico": 2,
    "básico": 2,
    "em desenvolvimento": 3,
    "em implantacao": 4,
    "em implantação": 4,
    "intermediario": 5,
    "intermediário": 5,
    "avancado": 6,
    "avançado": 6,
    "consolidado": 7,
    "sim": 7,
}


def estimar_nivel_indicador(valor):
    """Fallback de maturidade 0–7 quando não há coluna oficial pareada."""
    if pd.isna(valor):
        return None
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        nivel = float(valor)
        return nivel if 0 <= nivel <= 7 else None
    return NIVEIS_TEXTUAIS.get(normalizar_texto(valor))


def obter_nivel_indicador(nome_indicador, valor, linha_planilha=None):
    nm_col = MAPA_NIVEL_MATURIDADE.get(nome_indicador)
    if nm_col is not None and linha_planilha is not None and nm_col in linha_planilha.index:
        nivel_real = linha_planilha[nm_col]
        if not pd.isna(nivel_real):
            try:
                nivel_real = float(nivel_real)
                if 0 <= nivel_real <= 7:
                    return nivel_real
            except (TypeError, ValueError):
                pass
    return estimar_nivel_indicador(valor)
