import pytest

from municipio_analise.classificador import ClassificadorIndicadores, normalizar
from municipio_analise.models import IndicadorClassificado


class TestNormalizar:
    def test_remove_acentos_e_caixa(self):
        assert normalizar("Água e Esgoto") == "agua e esgoto"

    def test_aceita_numeros(self):
        assert normalizar(12345) == "12345"


class TestClassificarPorte:
    @pytest.mark.parametrize(
        "populacao,esperado",
        [
            (0, "pequeno porte"),
            (50_000, "pequeno porte"),
            (50_001, "médio porte"),
            (300_000, "médio porte"),
            (300_001, "grande porte"),
            (2_000_000, "grande porte"),
        ],
    )
    def test_limites_de_porte(self, populacao, esperado):
        assert ClassificadorIndicadores.classificar_porte(populacao) == esperado


class TestClassificarIndicador:
    @pytest.fixture
    def classificador(self):
        mapa = {
            normalizar("Índice da população total com atendimento de água"): IndicadorClassificado(
                dimensao="Econômica", topico="Água e Esgoto", chunk_id="economica_agua_e_esgoto"
            )
        }
        colunas_nao_indicadores = {normalizar("Município"), normalizar("Estado")}
        return ClassificadorIndicadores(mapa_indicadores=mapa, colunas_nao_indicadores=colunas_nao_indicadores)

    def test_correspondencia_exata_no_mapa(self, classificador):
        resultado = classificador.classificar_indicador("Índice da população total com atendimento de água")
        assert resultado.dimensao == "Econômica"
        assert resultado.chunk_id == "economica_agua_e_esgoto"

    def test_coluna_de_metadado_retorna_none(self, classificador):
        assert classificador.classificar_indicador("Município") is None
        assert classificador.nao_classificados == []

    def test_fallback_por_palavra_chave(self, classificador):
        resultado = classificador.classificar_indicador("Cobertura de banda larga no município")
        assert resultado is not None
        assert resultado.dimensao == "Econômica"
        assert resultado.chunk_id == "economica_conectividade"


    def test_fallback_semantico_por_embedding(self):
        from types import SimpleNamespace

        indice = SimpleNamespace()
        indice.similarity_search_with_relevance_scores = lambda nome, k=1: [(
            SimpleNamespace(metadata={
                "dimensao": "Meio Ambiente",
                "topico": "Áreas Verdes",
                "chunk_id": "meio_ambiente_areas_verdes",
            }),
            0.91,
        )]
        classificador = ClassificadorIndicadores(
            mapa_indicadores={},
            colunas_nao_indicadores=set(),
            indice_topicos=indice,
        )
        resultado = classificador.classificar_indicador("cobertura vegetal urbana monitorada")
        assert resultado is not None
        assert resultado.dimensao == "Meio Ambiente"
        assert resultado.chunk_id == "meio_ambiente_areas_verdes"

    def test_indicador_desconhecido_e_registrado(self, classificador):
        resultado = classificador.classificar_indicador("Indicador totalmente aleatório xyz123")
        assert resultado is None
        assert "Indicador totalmente aleatório xyz123" in classificador.nao_classificados

    def test_classificar_todos_agrupa_por_dimensao(self, classificador):
        indicadores = {
            "Índice da população total com atendimento de água": 80,
            "Município": "Congonhas",
        }
        agrupado = classificador.classificar_todos(indicadores)
        assert "Econômica" in agrupado
        assert agrupado["Econômica"] == {"Índice da população total com atendimento de água": 80}
