"""Serviço assíncrono de geração das análises via Gemini/LangChain."""
from __future__ import annotations

import asyncio
import logging

from langchain_google_genai import ChatGoogleGenerativeAI

from .config import Config
from .exceptions import RespostaInvalidaError, TentativasEsgotadasError
from .models import AnaliseDimensao, AnaliseDimensaoResultado, AnaliseGeral, ChunkCarta
from .prompts import (
    INSTRUCAO_COM_BASE,
    INSTRUCAO_SEM_BASE,
    formatar_chunks,
    formatar_dados_contextuais,
    formatar_indicadores,
    prompt_dimensao,
    prompt_geral,
)

logger = logging.getLogger(__name__)


class LLMAnaliseService:
    def __init__(self, config: Config):
        self._config = config
        self._llm = ChatGoogleGenerativeAI(
            model=config.modelo,
            google_api_key=config.validar_api_key(),
            temperature=config.temperature,
            top_p=config.top_p,
            max_output_tokens=config.max_output_tokens,
        )
        self._chain_geral = prompt_geral | self._llm.with_structured_output(AnaliseGeral)
        self._chain_dimensao = prompt_dimensao | self._llm.with_structured_output(AnaliseDimensao)

    @staticmethod
    def _instrucao_base(chunks: list[ChunkCarta]) -> str:
        if chunks:
            return INSTRUCAO_COM_BASE.format(base_conceitual=formatar_chunks(chunks))
        return INSTRUCAO_SEM_BASE

    async def gerar_analise_geral(
        self,
        municipio: str,
        porte: str,
        indicadores: dict[str, object],
        chunks_gerais: list[ChunkCarta],
        dados_contextuais: dict[str, object] | None = None,
    ) -> str:
        instrucao_base = self._instrucao_base(chunks_gerais)
        indicadores_txt = formatar_indicadores(indicadores)
        dados_contextuais_txt = formatar_dados_contextuais(dados_contextuais or {})

        ultimo_erro: Exception | None = None
        for tentativa in range(1, self._config.tentativas_llm + 1):
            try:
                resultado = await self._chain_geral.ainvoke(
                    {
                        "municipio": municipio,
                        "porte": porte,
                        "indicadores_txt": indicadores_txt,
                        "instrucao_base": instrucao_base,
                        "dados_contextuais_txt": dados_contextuais_txt,
                    }
                )
                if not resultado.analise_geral or len(resultado.analise_geral.strip()) < 40:
                    raise RespostaInvalidaError("Resposta do modelo vazia ou incompleta.")
                return resultado.analise_geral
            except Exception as exc:
                ultimo_erro = exc
                logger.warning("Falha ao gerar análise geral (tentativa %d): %s", tentativa, exc)

        raise TentativasEsgotadasError(
            f"Não foi possível gerar a análise geral após {self._config.tentativas_llm} tentativas: {ultimo_erro}"
        ) from ultimo_erro

    async def gerar_analise_dimensao(
        self,
        dimensao: str,
        municipio: str,
        porte: str,
        indicadores_dimensao: dict[str, object],
        chunks_selecionados: list[ChunkCarta],
        dados_contextuais_dimensao: dict[str, object] | None = None,
    ) -> AnaliseDimensaoResultado:
        if not indicadores_dimensao:
            raise RespostaInvalidaError(f"A dimensão '{dimensao}' não possui indicadores associados.")

        instrucao_base = self._instrucao_base(chunks_selecionados)
        indicadores_txt = formatar_indicadores(indicadores_dimensao)
        dados_contextuais_txt = formatar_dados_contextuais(dados_contextuais_dimensao or {})

        ultimo_erro: Exception | None = None
        for tentativa in range(1, self._config.tentativas_llm + 1):
            try:
                resultado = await self._chain_dimensao.ainvoke(
                    {
                        "municipio": municipio,
                        "porte": porte,
                        "dimensao": dimensao,
                        "indicadores_txt": indicadores_txt,
                        "instrucao_base": instrucao_base,
                        "dados_contextuais_txt": dados_contextuais_txt,
                    }
                )
                if len(resultado.sugestoes) != 3:
                    raise RespostaInvalidaError(
                        f"Modelo retornou {len(resultado.sugestoes)} sugestões (esperado: 3)."
                    )
                if not resultado.analise or len(resultado.analise.strip()) < 30:
                    raise RespostaInvalidaError("Análise da dimensão vazia ou incompleta.")
                return AnaliseDimensaoResultado(
                    dimensao=dimensao,
                    analise=resultado.analise,
                    sugestoes=resultado.sugestoes,
                )
            except Exception as exc:
                ultimo_erro = exc
                logger.warning("Falha ao gerar análise de '%s' (tentativa %d): %s", dimensao, tentativa, exc)

        raise TentativasEsgotadasError(
            f"Não foi possível gerar a análise de '{dimensao}' após {self._config.tentativas_llm} tentativas: {ultimo_erro}"
        ) from ultimo_erro

    async def gerar_todas_dimensoes(
        self,
        municipio: str,
        porte: str,
        indicadores_por_dimensao: dict[str, dict[str, object]],
        chunks_por_dimensao: dict[str, list[ChunkCarta]],
        dados_contextuais_por_dimensao: dict[str, dict[str, object]] | None = None,
    ) -> dict[str, AnaliseDimensaoResultado]:
        dados_contextuais_por_dimensao = dados_contextuais_por_dimensao or {}
        dimensoes = list(indicadores_por_dimensao.keys())
        tarefas = [
            self.gerar_analise_dimensao(
                dimensao=dimensao,
                municipio=municipio,
                porte=porte,
                indicadores_dimensao=indicadores_por_dimensao[dimensao],
                chunks_selecionados=chunks_por_dimensao.get(dimensao, []),
                dados_contextuais_dimensao=dados_contextuais_por_dimensao.get(dimensao, {}),
            )
            for dimensao in dimensoes
        ]
        resultados = await asyncio.gather(*tarefas, return_exceptions=True)

        saida: dict[str, AnaliseDimensaoResultado] = {}
        erros: list[str] = []
        for dimensao, resultado in zip(dimensoes, resultados):
            if isinstance(resultado, Exception):
                erros.append(f"{dimensao}: {resultado}")
            else:
                saida[dimensao] = resultado

        if erros:
            raise TentativasEsgotadasError(
                "Falha ao gerar uma ou mais dimensões: " + "; ".join(erros)
            )
        return saida
