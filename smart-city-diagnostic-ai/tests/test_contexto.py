import pandas as pd

from municipio_analise.contexto import obter_dados_contextuais
from municipio_analise.utils import normalizar_coluna


def test_contexto_economico():
    linha = pd.Series({normalizar_coluna("PIB per capita do município"): 12345})
    dados = obter_dados_contextuais("Econômica", linha)
    assert dados["PIB per capita do município"] == 12345
