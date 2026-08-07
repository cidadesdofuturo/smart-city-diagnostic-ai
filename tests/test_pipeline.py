import pandas as pd

from municipio_analise import Config, PipelineAnaliseMunicipio
from municipio_analise.utils import normalizar_coluna


class FakeLLM:
    def pesquisar_contexto_municipio(self, municipio, estado=None, codigo_ibge=None):
        assert municipio == "Cidade Teste"
        assert estado == "MG"
        assert codigo_ibge == "3100000"
        return "Contexto web validado."

    def pesquisar_validacao_dimensao(self, **kwargs):
        assert kwargs["indicadores_dimensao"]
        assert kwargs["estado"] == "MG"
        assert kwargs["codigo_ibge"] == "3100000"
        return f"Validação web de {kwargs['dimensao']}."

    def gerar_analise_geral(
        self,
        municipio,
        porte,
        indicadores,
        chunks_gerais,
        dados_contextuais=None,
        pesquisa_web=None,
    ):
        assert municipio == "Cidade Teste"
        assert indicadores
        assert chunks_gerais
        assert pesquisa_web == "Contexto web validado."
        return (
            "Parágrafo positivo suficientemente completo.\n\n"
            "Parágrafo de desafios suficientemente completo."
        )

    def gerar_analise_dimensao(self, **kwargs):
        assert kwargs["indicadores_dimensao"]
        assert kwargs["chunks_selecionados"]
        assert kwargs["pesquisa_web_dimensao"].startswith("Validação web")
        return {
            "analise": (
                f"Primeiro parágrafo suficientemente completo de {kwargs['dimensao']}.\n\n"
                f"Segundo parágrafo suficientemente completo de {kwargs['dimensao']}."
            ),
            "sugestoes": [
                "Sugestão 1",
                "Sugestão 2",
                "Sugestão 3",
                "Sugestão 4",
            ],
        }


def test_pipeline_orquestra_quatro_dimensoes_com_validacao_web_sem_chamar_api(tmp_path):
    cfg = Config(base_path=tmp_path, api_key="teste")
    pipeline = PipelineAnaliseMunicipio(cfg)
    pipeline._llm = FakeLLM()

    bruto = {
        "Município": "Cidade Teste",
        "População total estimada do município": 100_000,
        "Estado": "MG",
        "Cod Municipio": 3100000,
        "Cobertura de fibra ótica": 90,
        "N M Indicador.18": 6,
        "Taxa de analfabetismo": 4,
        "N M Indicador.32": 5,
        "Monitoramento da qualidade do ar": "sim",
        "N M Indicador.71": 7,
        "Planejamento Estratégico para Transformação Digital": "em desenvolvimento",
        "N M Indicador.76": 3,
    }
    pipeline.df = pd.DataFrame([
        {normalizar_coluna(k): v for k, v in bruto.items()}
    ])

    relatorio = pipeline.analisar_municipio("Cidade Teste")

    assert set(relatorio["dimensoes"]) == {
        "economica",
        "sociocultural",
        "meio_ambiente",
        "capacidades_institucionais",
    }
    assert all(len(bloco["sugestoes"]) == 4 for bloco in relatorio["dimensoes"].values())
    assert relatorio["metadados"]["escala_maturidade"] == "0-7"
    assert relatorio["metadados"]["modelo"] == "gemini-3.6-flash"
    assert relatorio["metadados"]["codigo_ibge"] == "3100000"
