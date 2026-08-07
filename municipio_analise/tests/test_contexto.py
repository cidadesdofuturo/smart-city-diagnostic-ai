import pandas as pd

from municipio_analise.contexto import DadosContextuaisRepository


def test_obter_dados_contextuais_por_dimensao():
    repo = DadosContextuaisRepository(
        {
            "pib per capita do municipio": {"dimensao": "Econômica", "rotulo": "PIB per capita do município"},
            "indice de gini": {"dimensao": "Sociocultural", "rotulo": "Índice de GINI"},
        }
    )
    linha = pd.Series({"pib per capita do municipio": 123, "indice de gini": 0.4})

    assert repo.obter_por_dimensao("Econômica", linha) == {"PIB per capita do município": 123}
    assert repo.obter_por_dimensao("Sociocultural", linha) == {"Índice de GINI": 0.4}


def test_dado_contextual_nulo_e_ignorado():
    repo = DadosContextuaisRepository(
        {"capag": {"dimensao": "Econômica", "rotulo": "CAPAG"}}
    )
    linha = pd.Series({"capag": float("nan")})
    assert repo.obter_por_dimensao("Econômica", linha) == {}
