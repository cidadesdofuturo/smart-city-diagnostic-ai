from municipio_analise.modelos import AnaliseDimensao


def test_dimensao_aceita_terceiro_paragrafo_opcional():
    x = AnaliseDimensao(paragrafo_1="a", paragrafo_2="b", paragrafo_3=None, sugestoes=["1","2","3","4"])
    assert x.paragrafo_3 is None
    y = AnaliseDimensao(paragrafo_1="a", paragrafo_2="b", paragrafo_3="c", sugestoes=["1","2","3","4"])
    assert y.paragrafo_3 == "c"
