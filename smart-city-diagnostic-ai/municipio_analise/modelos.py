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
            "Exatamente dois parágrafos institucionais sobre a dimensão. "
            "O primeiro apresenta a situação atual e os resultados favoráveis; "
            "o segundo interpreta os principais desafios, contrastes e lacunas, "
            "sem repetir o primeiro parágrafo."
        )
    )
    sugestoes: List[str] = Field(
        description=(
            "Exatamente quatro sugestões de melhoria, distintas entre si, "
            "realistas, diretamente relacionadas aos indicadores e compatíveis "
            "com o porte do município."
        )
    )
