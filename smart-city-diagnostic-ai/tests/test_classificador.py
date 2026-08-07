from municipio_analise.classificador import ClassificadorIndicadores


def test_classificacao_exata_sem_api():
    c = ClassificadorIndicadores()
    r = c.classificar("Cobertura de fibra ótica")
    assert r["dimensao"] == "Econômica"
    assert r["chunk_id"] == "economica_conectividade"


def test_coluna_de_contexto_nao_vira_indicador():
    c = ClassificadorIndicadores()
    assert c.classificar("PIB per capita do município") is None
