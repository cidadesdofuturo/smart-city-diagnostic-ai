from __future__ import annotations

import re
import unicodedata


def classificar_porte(populacao: int | float) -> str:
    if populacao <= 50_000:
        return "pequeno porte"
    if populacao <= 300_000:
        return "médio porte"
    return "grande porte"


def normalizar_texto(texto) -> str:
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = texto.encode("ascii", errors="ignore").decode("utf-8")
    return texto.lower()


def normalizar_coluna(texto) -> str:
    return normalizar_texto(str(texto).strip())


def nome_arquivo_seguro(texto: str) -> str:
    nome = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    nome = re.sub(r"[^A-Za-z0-9._-]+", "_", nome).strip("_")
    return nome or "municipio"


def separar_paragrafos(texto: str) -> list[str]:
    """Separa parágrafos reais, tolerando espaços nas linhas em branco."""
    return [p.strip() for p in re.split(r"\n\s*\n", texto.strip()) if p.strip()]
