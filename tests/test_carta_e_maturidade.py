import pandas as pd
import pytest

from municipio_analise.carta import CartaRepository
from municipio_analise.classificador import ClassificadorIndicadores
from municipio_analise.exceptions import ChunkNaoEncontradoError
from municipio_analise.maturidade import GestorMaturidade
from municipio_analise.models import ChunkCarta, IndicadorClassificado


@pytest.fixture
def carta():
    chunks = {
        "geral_conceito_brasileiro_de_cidades_inteligentes": ChunkCarta(
            chunk_id="geral_conceito_brasileiro_de_cidades_inteligentes",
            dimensao="Geral",
            topico="Conceito",
            texto="texto geral",
            fonte="Carta",
        ),
        "economica_conectividade": ChunkCarta(
            chunk_id="economica_conectividade",
            dimensao="Econômica",
            topico="Conectividade",
            texto="texto conectividade",
            fonte="Carta",
        ),
    }
    return CartaRepository(chunks=chunks, topicos_sem_chunk=["economica_transporte"])


class TestCartaRepository:
    def test_obter_chunk_existente(self, carta):
        chunk = carta.obter("geral_conceito_brasileiro_de_cidades_inteligentes")
        assert chunk.texto == "texto geral"

    def test_obter_chunk_inexistente_levanta_erro(self, carta):
        with pytest.raises(ChunkNaoEncontradoError):
            carta.obter("chunk_que_nao_existe")

    def test_obter_opcional_retorna_none(self, carta):
        assert carta.obter_opcional("chunk_que_nao_existe") is None

    def test_chunks_gerais_ignora_topicos_ausentes(self, carta):
        resultado = carta.chunks_gerais(["conceito_brasileiro_de_cidades_inteligentes", "topico_sem_chunk"])
        assert len(resultado) == 1
        assert resultado[0].chunk_id == "geral_conceito_brasileiro_de_cidades_inteligentes"

    def test_len_e_contains(self, carta):
        assert len(carta) == 2
        assert "geral_conceito_brasileiro_de_cidades_inteligentes" in carta
        assert "inexistente" not in carta


class TestGestorMaturidade:
    @pytest.fixture
    def classificador(self):
        mapa = {
            "cobertura de fibra otica": IndicadorClassificado(
                dimensao="Econômica", topico="Conectividade", chunk_id="economica_conectividade"
            )
        }
        return ClassificadorIndicadores(mapa_indicadores=mapa, colunas_nao_indicadores=set())

    @pytest.fixture
    def gestor(self, carta, classificador):
        return GestorMaturidade(carta=carta, classificador=classificador, mapa_nivel_maturidade={})

    def test_estimar_nivel_por_valor_numerico(self, gestor):
        assert gestor.estimar_nivel_por_valor(3) == 3.0

    def test_estimar_nivel_por_valor_textual(self, gestor):
        assert gestor.estimar_nivel_por_valor("Avançado") == 4

    def test_estimar_nivel_por_valor_nulo(self, gestor):
        assert gestor.estimar_nivel_por_valor(float("nan")) is None

    def test_obter_nivel_usa_coluna_da_planilha_quando_disponivel(self, carta, classificador):
        gestor = GestorMaturidade(
            carta=carta,
            classificador=classificador,
            mapa_nivel_maturidade={"cobertura de fibra otica": "n m indicador"},
        )
        linha = pd.Series({"n m indicador": 5})
        assert gestor.obter_nivel("Cobertura de Fibra Ótica", "avançado", linha) == 5.0

    def test_selecionar_chunks_dimensao_inclui_gerais_e_setoriais(self, gestor):
        chunks = gestor.selecionar_chunks_dimensao(
            "Econômica", {"Cobertura de Fibra Ótica": "avançado"}
        )
        chunk_ids = {c.chunk_id for c in chunks}
        assert "geral_conceito_brasileiro_de_cidades_inteligentes" in chunk_ids
        assert "economica_conectividade" in chunk_ids

    def test_selecionar_chunks_dimensao_nao_mistura_outra_dimensao(self, gestor):
        chunks = gestor.selecionar_chunks_dimensao(
            "Sociocultural", {"Cobertura de Fibra Ótica": "avançado"}
        )
        chunk_ids = {c.chunk_id for c in chunks}
        assert "economica_conectividade" not in chunk_ids

    def test_fallback_semantico_para_topico_sem_chunk(self, carta):
        from types import SimpleNamespace

        mapa = {
            "mobilidade compartilhada": IndicadorClassificado(
                dimensao="Econômica", topico="Transporte", chunk_id="economica_transporte"
            )
        }
        classificador = ClassificadorIndicadores(mapa_indicadores=mapa, colunas_nao_indicadores=set())
        indice = SimpleNamespace()
        indice.similarity_search = lambda *args, **kwargs: [
            SimpleNamespace(metadata={"chunk_id": "economica_conectividade"})
        ]
        gestor = GestorMaturidade(
            carta=carta,
            classificador=classificador,
            mapa_nivel_maturidade={},
            indice_chunks=indice,
        )
        chunks = gestor.selecionar_chunks_dimensao(
            "Econômica", {"mobilidade compartilhada": "inicial"}
        )
        assert "economica_conectividade" in {c.chunk_id for c in chunks}
