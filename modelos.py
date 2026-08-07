"""Modelos Pydantic usados na saída estruturada do LLM."""
from typing import List

from pydantic import BaseModel, Field


class AnaliseGeral(BaseModel):
    analise_geral: str = Field(
        description=(
            "Dois parágrafos: pontos positivos e depois desafios/limitações, "
            "sem citar números nem o porte do município."
        )
    )


class AnaliseDimensao(BaseModel):
    analise: str = Field(
        description=(
            "Um parágrafo institucional sobre a dimensão, majoritariamente positivo, "
            "com apontamentos críticos sutis."
        )
    )
    sugestoes: List[str] = Field(
        description=(
            "Exatamente três sugestões de melhoria, realistas e compatíveis com o porte do município."
        )
    )
