from collections import Counter

from municipio_analise.carta_granular import preparar_documentos_carta


def test_snapshot_granular_tem_185_documentos():
    documentos = preparar_documentos_carta()
    assert len(documentos) == 185
    tipos = Counter(doc["tipo"] for doc in documentos)
    assert tipos == {
        "conceito": 3,
        "principio": 5,
        "diretriz": 6,
        "contexto_objetivo": 8,
        "recomendacao": 163,
    }
