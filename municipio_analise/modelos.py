from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class AnaliseGeral(BaseModel):
    analise_geral: str = Field(description="Dois parágrafos: pontos positivos e depois desafios/limitações, sem citar números nem o porte do município.")


class AnaliseDimensao(BaseModel):
    paragrafo_1: str = Field(description="Situação atual, capacidades existentes e resultados favoráveis, sem sugestões.")
    paragrafo_2: str = Field(description="Principais desafios, contrastes e lacunas, sem repetir o primeiro parágrafo.")
    paragrafo_3: Optional[str] = Field(default=None, description="Terceiro parágrafo opcional para aprofundar uma frente realmente distinta.")
    sugestoes: List[str] = Field(description="Exatamente quatro sugestões distintas, realistas e relacionadas aos indicadores.")


class RevisaoDimensao(BaseModel):
    paragrafo_1: str
    paragrafo_2: str
    paragrafo_3: Optional[str] = None
    sugestoes: List[str]
