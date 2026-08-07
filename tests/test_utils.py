from municipio_analise.utils import classificar_porte, normalizar_coluna


def test_normalizar_coluna():
    assert normalizar_coluna("  Cobertura de Fibra Ótica ") == "cobertura de fibra otica"


def test_classificar_porte():
    assert classificar_porte(50_000) == "pequeno porte"
    assert classificar_porte(50_001) == "médio porte"
    assert classificar_porte(300_001) == "grande porte"
