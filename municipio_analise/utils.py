from __future__ import annotations

import re
import unicodedata


def normalizar_texto(texto) -> str:
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = texto.encode("ascii", errors="ignore").decode("utf-8")
    return texto.lower().strip()


def normalizar_coluna(texto) -> str:
    return normalizar_texto(texto)


def classificar_porte(populacao: int | float) -> str:
    populacao = float(populacao)
    if populacao <= 50_000:
        return "pequeno porte"
    if populacao <= 300_000:
        return "médio porte"
    return "grande porte"


def separar_paragrafos(texto: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", (texto or "").strip()) if p.strip()]
