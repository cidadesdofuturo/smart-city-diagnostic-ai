from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from municipio_analise.config import Config
from municipio_analise.exceptions import TentativasEsgotadasError
from municipio_analise.models import AnaliseDimensao, AnaliseGeral, ChunkCarta


@pytest.fixture
def config():
    return Config(api_key="fake-key")


def _mock_chain(retorno=None, excecao=None):
    """Cria uma chain fake cujo .ainvoke() retorna `retorno` ou levanta `excecao`."""
    chain = MagicMock()
    if excecao is not None:
        chain.ainvoke = AsyncMock(side_effect=excecao)
    else:
        chain.ainvoke = AsyncMock(return_value=retorno)
    return chain


@pytest.fixture
def servico(config):
    with patch("municipio_analise.llm_service.ChatGoogleGenerativeAI"):
        from municipio_analise.llm_service import LLMAnaliseService

        return LLMAnaliseService(config)


class TestGerarAnaliseGeral:
    @pytest.mark.asyncio
    async def test_retorna_texto_quando_resposta_valida(self, servico):
        resposta = AnaliseGeral(analise_geral="x" * 50)
        servico._chain_geral = _mock_chain(retorno=resposta)

        resultado = await servico.gerar_analise_geral("Congonhas", "médio porte", {"ind": 1}, [])
        assert resultado == "x" * 50


    @pytest.mark.asyncio
    async def test_inclui_dados_contextuais_no_prompt(self, servico):
        resposta = AnaliseGeral(analise_geral="x" * 50)
        servico._chain_geral = _mock_chain(retorno=resposta)

        await servico.gerar_analise_geral(
            "Congonhas",
            "médio porte",
            {"ind": 1},
            [],
            dados_contextuais={"PIB per capita do município": 123},
        )
        payload = servico._chain_geral.ainvoke.await_args.args[0]
        assert "PIB per capita do município: 123" in payload["dados_contextuais_txt"]

    @pytest.mark.asyncio
    async def test_levanta_erro_apos_esgotar_tentativas(self, servico):
        servico._chain_geral = _mock_chain(excecao=RuntimeError("falha de rede"))
        servico._config.tentativas_llm = 2

        with pytest.raises(TentativasEsgotadasError):
            await servico.gerar_analise_geral("Congonhas", "médio porte", {"ind": 1}, [])
        assert servico._chain_geral.ainvoke.await_count == 2

    @pytest.mark.asyncio
    async def test_resposta_curta_demais_e_rejeitada_e_tenta_de_novo(self, servico):
        servico._chain_geral = _mock_chain(retorno=AnaliseGeral(analise_geral="curto"))
        servico._config.tentativas_llm = 1

        with pytest.raises(TentativasEsgotadasError):
            await servico.gerar_analise_geral("Congonhas", "médio porte", {"ind": 1}, [])


class TestGerarAnaliseDimensao:
    @pytest.mark.asyncio
    async def test_retorna_resultado_com_tres_sugestoes(self, servico):
        resposta = AnaliseDimensao(analise="x" * 40, sugestoes=["a", "b", "c"])
        servico._chain_dimensao = _mock_chain(retorno=resposta)

        resultado = await servico.gerar_analise_dimensao(
            "Econômica", "Congonhas", "médio porte", {"ind": 1}, []
        )
        assert resultado.dimensao == "Econômica"
        assert len(resultado.sugestoes) == 3

    @pytest.mark.asyncio
    async def test_sem_indicadores_levanta_erro_sem_chamar_llm(self, servico):
        servico._chain_dimensao = _mock_chain(retorno=None)
        with pytest.raises(Exception):
            await servico.gerar_analise_dimensao("Econômica", "Congonhas", "médio porte", {}, [])
        servico._chain_dimensao.ainvoke.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_numero_errado_de_sugestoes_e_rejeitado(self, servico):
        resposta = AnaliseDimensao(analise="x" * 40, sugestoes=["a", "b"])
        servico._chain_dimensao = _mock_chain(retorno=resposta)
        servico._config.tentativas_llm = 1

        with pytest.raises(TentativasEsgotadasError):
            await servico.gerar_analise_dimensao("Econômica", "Congonhas", "médio porte", {"ind": 1}, [])


class TestGerarTodasDimensoes:
    @pytest.mark.asyncio
    async def test_executa_em_paralelo_e_agrega_resultados(self, servico):
        async def fake_gerar_analise_dimensao(dimensao, **kwargs):
            from municipio_analise.models import AnaliseDimensaoResultado

            return AnaliseDimensaoResultado(dimensao=dimensao, analise="ok" * 20, sugestoes=["a", "b", "c"])

        servico.gerar_analise_dimensao = fake_gerar_analise_dimensao

        resultado = await servico.gerar_todas_dimensoes(
            "Congonhas",
            "médio porte",
            {"Econômica": {"ind": 1}, "Sociocultural": {"ind": 2}},
            {},
        )
        assert set(resultado.keys()) == {"Econômica", "Sociocultural"}

    @pytest.mark.asyncio
    async def test_uma_dimensao_falhando_levanta_erro_agregado(self, servico):
        async def fake_gerar_analise_dimensao(dimensao, **kwargs):
            if dimensao == "Sociocultural":
                raise TentativasEsgotadasError("falhou")
            from municipio_analise.models import AnaliseDimensaoResultado

            return AnaliseDimensaoResultado(dimensao=dimensao, analise="ok" * 20, sugestoes=["a", "b", "c"])

        servico.gerar_analise_dimensao = fake_gerar_analise_dimensao

        with pytest.raises(TentativasEsgotadasError):
            await servico.gerar_todas_dimensoes(
                "Congonhas",
                "médio porte",
                {"Econômica": {"ind": 1}, "Sociocultural": {"ind": 2}},
                {},
            )
