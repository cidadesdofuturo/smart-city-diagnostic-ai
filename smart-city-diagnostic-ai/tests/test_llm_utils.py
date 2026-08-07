from types import SimpleNamespace

from municipio_analise.llm_service import extrair_texto_resposta, normalizar_codigo_ibge
from municipio_analise.utils import separar_paragrafos


def test_normalizar_codigo_ibge_float_excel():
    assert normalizar_codigo_ibge(3171303.0) == "3171303"


def test_normalizar_codigo_ibge_ausente():
    assert normalizar_codigo_ibge(float("nan")) is None


def test_extrair_texto_resposta_de_blocos():
    resposta = SimpleNamespace(
        text=None,
        content=[
            {"type": "text", "text": "Primeiro"},
            {"type": "text", "text": "Segundo"},
        ],
    )
    assert extrair_texto_resposta(resposta) == "Primeiro\nSegundo"


def test_separar_exatamente_dois_paragrafos():
    assert separar_paragrafos("Um.\n  \nDois.") == ["Um.", "Dois."]
