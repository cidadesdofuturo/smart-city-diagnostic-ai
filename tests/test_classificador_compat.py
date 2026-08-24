from municipio_analise.classificador import ClassificadorIndicadores


def test_api_antiga_com_fallback_callable_continua_funcionando():
    esperado = {"dimensao": "Econômica", "topico": "Teste", "chunk_id": "x"}
    classificador = ClassificadorIndicadores(lambda _: esperado)

    assert classificador.classificar("indicador totalmente inventado xyz") == esperado


def test_alias_e_limpeza_de_nao_classificados():
    classificador = ClassificadorIndicadores()
    assert classificador.classificar("indicador totalmente inventado xyz") is None
    assert classificador.nao_classificados == classificador.indicadores_nao_classificados
    assert classificador.nao_classificados

    classificador.limpar_nao_classificados()
    assert classificador.nao_classificados == []
