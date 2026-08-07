from municipio_analise.dados import (
    CHUNKS_CARTA,
    DADOS_CONTEXTUAIS_BRUTO,
    MAPA_INDICADORES_BRUTO,
    MAPA_NIVEL_MATURIDADE_BRUTO,
)


def test_contagens_extraidas_do_notebook_fonte():
    assert len(CHUNKS_CARTA) == 20
    assert len(MAPA_INDICADORES_BRUTO) == 85
    assert len(MAPA_NIVEL_MATURIDADE_BRUTO) == 88
    assert len(DADOS_CONTEXTUAIS_BRUTO) == 23
