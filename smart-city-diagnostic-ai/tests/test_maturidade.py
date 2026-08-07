from municipio_analise.maturidade import estimar_nivel_indicador


def test_escala_numerica_zero_a_sete():
    assert estimar_nivel_indicador(0) == 0.0
    assert estimar_nivel_indicador(7) == 7.0
    assert estimar_nivel_indicador(8) is None
    assert estimar_nivel_indicador(97.5) is None


def test_escala_textual_zero_a_sete():
    assert estimar_nivel_indicador("inexistente") == 0
    assert estimar_nivel_indicador("intermediário") == 5
    assert estimar_nivel_indicador("avançado") == 6
    assert estimar_nivel_indicador("consolidado") == 7
