"""Orquestrador do pipeline completo de análise municipal."""
from __future__ import annotations

import logging

from .carta import CartaRepository
from .classificador import ClassificadorIndicadores
from .config import Config
from .contexto import DadosContextuaisRepository
from .data.dimensoes import CHUNKS_GERAIS, DIMENSAO_PARA_CHAVE, DIMENSOES
from .embeddings_service import GestorEmbeddings
from .exceptions import DimensaoSemIndicadoresError
from .llm_service import LLMAnaliseService
from .maturidade import GestorMaturidade
from .models import RelatorioMunicipio
from .planilha import LeitorPlanilha
from .relatorio import GeradorRelatorioWord

logger = logging.getLogger(__name__)


class PipelineAnaliseMunicipio:
    """Coordena a geração completa do relatório institucional de um município."""

    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        self.leitor = LeitorPlanilha(self.config)
        self.carta = CartaRepository.carregar_padrao()
        self.contexto = DadosContextuaisRepository.carregar_padrao()

        indice_topicos = None
        indice_chunks = None
        self.gestor_embeddings = None
        if self.config.usar_embeddings_semanticos:
            self.gestor_embeddings = GestorEmbeddings(self.config, self.carta)
            indice_topicos = self.gestor_embeddings.indice_topicos()
            indice_chunks = self.gestor_embeddings.indice_chunks()

        self.classificador = ClassificadorIndicadores.carregar_padrao(
            indice_topicos=indice_topicos
        )
        self.gestor_maturidade = GestorMaturidade.carregar_padrao(
            self.carta,
            self.classificador,
            indice_chunks=indice_chunks,
        )
        self.llm_service = LLMAnaliseService(self.config)
        self.gerador_relatorio = GeradorRelatorioWord(self.config)

    def carregar_planilha(self) -> "PipelineAnaliseMunicipio":
        self.leitor.carregar()
        return self

    async def analisar_municipio(self, municipio: str) -> RelatorioMunicipio:
        linha = self.leitor.obter_linha_municipio(municipio)
        populacao = int(linha[self.config.coluna_populacao])
        porte = ClassificadorIndicadores.classificar_porte(populacao)
        logger.info("Porte identificado para %s: %s", municipio, porte)

        candidatos = self.leitor.obter_indicadores_candidatos(linha)
        indicadores_por_dimensao = self.classificador.classificar_todos(candidatos)

        for dimensao in DIMENSOES:
            if not indicadores_por_dimensao[dimensao]:
                logger.warning("Dimensão '%s' ficou sem indicadores classificados.", dimensao)

        if self.classificador.nao_classificados:
            logger.warning(
                "Indicadores não classificados (revisar mapa): %s",
                sorted(set(self.classificador.nao_classificados)),
            )

        todos_indicadores = {
            nome: valor
            for indicadores in indicadores_por_dimensao.values()
            for nome, valor in indicadores.items()
        }

        dados_contextuais_por_dimensao = {
            dimensao: self.contexto.obter_por_dimensao(dimensao, linha)
            for dimensao in DIMENSOES
        }
        todos_dados_contextuais = self.contexto.obter_todos(DIMENSOES, linha)

        chunks_gerais = self.carta.chunks_gerais(CHUNKS_GERAIS)
        analise_geral = await self.llm_service.gerar_analise_geral(
            municipio,
            porte,
            todos_indicadores,
            chunks_gerais,
            dados_contextuais=todos_dados_contextuais,
        )

        chunks_por_dimensao = {
            dimensao: self.gestor_maturidade.selecionar_chunks_dimensao(
                dimensao,
                indicadores_por_dimensao[dimensao],
                linha,
            )
            for dimensao in DIMENSOES
            if indicadores_por_dimensao[dimensao]
        }

        indicadores_validos = {
            dimensao: valores
            for dimensao, valores in indicadores_por_dimensao.items()
            if valores
        }
        if not indicadores_validos:
            raise DimensaoSemIndicadoresError(
                f"Nenhuma dimensão possui indicadores classificados para '{municipio}'."
            )

        resultados_dimensao = await self.llm_service.gerar_todas_dimensoes(
            municipio,
            porte,
            indicadores_validos,
            chunks_por_dimensao,
            dados_contextuais_por_dimensao=dados_contextuais_por_dimensao,
        )

        relatorio = RelatorioMunicipio(
            municipio=municipio,
            porte=porte,
            analise_geral=analise_geral,
        )
        for dimensao, resultado in resultados_dimensao.items():
            chave = DIMENSAO_PARA_CHAVE[dimensao]
            relatorio.dimensoes[chave] = resultado
        return relatorio

    def salvar_relatorio(self, relatorio: RelatorioMunicipio) -> str:
        return self.gerador_relatorio.gerar(relatorio)
