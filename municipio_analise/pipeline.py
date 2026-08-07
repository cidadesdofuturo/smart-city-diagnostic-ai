from __future__ import annotations

import pandas as pd

from .classificador import ClassificadorIndicadores
from .config import Config
from .contexto import obter_dados_contextuais, obter_todos_dados_contextuais
from .dados import CHUNKS_CARTA
from .embeddings_service import EmbeddingsService
from .llm_service import LLMService, normalizar_codigo_ibge
from .planilha import carregar_planilha, listar_municipios, obter_linha_municipio
from .relatorio import gerar_relatorio_word
from .seletor_chunks import SeletorChunks
from .taxonomia import CHUNKS_GERAIS, DIMENSAO_PARA_CHAVE, DIMENSOES
from .utils import classificar_porte


class PipelineAnaliseMunicipio:
    """Orquestra o fluxo completo do notebook-fonte em uma única API."""

    def __init__(self, config: Config):
        self.config = config
        self.df = None
        self.embeddings = EmbeddingsService(config)
        self.classificador = ClassificadorIndicadores(self.embeddings.classificar_topico)
        self.seletor = SeletorChunks(self.classificador, self.embeddings)
        self._llm = None

    @property
    def llm(self):
        if self._llm is None:
            self.config.validar(exigir_planilha=False, exigir_api=True)
            self._llm = LLMService(self.config)
        return self._llm

    def carregar_planilha(self):
        self.df = carregar_planilha(self.config)
        return self.df

    def municipios(self) -> list[str]:
        if self.df is None:
            self.carregar_planilha()
        return listar_municipios(self.df, self.config.coluna_municipio)

    def analisar_municipio(self, municipio: str) -> dict:
        if self.df is None:
            self.carregar_planilha()

        self.classificador.limpar_nao_classificados()
        dados = obter_linha_municipio(self.df, self.config.coluna_municipio, municipio)
        populacao = int(dados[self.config.coluna_populacao])
        porte = classificar_porte(populacao)
        estado = dados.get("estado", None)
        codigo_ibge = normalizar_codigo_ibge(dados.get("cod municipio", None))

        colunas_ignoradas = {
            self.config.coluna_municipio,
            self.config.coluna_populacao,
            "cod municipio",
            "estado",
            "avaliada",
        }
        candidatos = {
            nome: valor
            for nome, valor in dados.items()
            if nome not in colunas_ignoradas
        }

        indicadores_por_dimensao = {d: {} for d in DIMENSOES}
        for nome, valor in candidatos.items():
            # Mantido da reconstrução anterior: ausência de dado não é evidência
            # de baixa maturidade e não deve aparecer como "nan" no prompt.
            if pd.isna(valor):
                continue
            classificacao = self.classificador.classificar(nome)
            if classificacao:
                indicadores_por_dimensao[classificacao["dimensao"]][nome] = valor

        todos_indicadores = {
            nome: valor
            for indicadores in indicadores_por_dimensao.values()
            for nome, valor in indicadores.items()
        }

        dados_contextuais_por_dimensao = {
            dimensao: obter_dados_contextuais(dimensao, dados) for dimensao in DIMENSOES
        }
        todos_dados_contextuais = obter_todos_dados_contextuais(dados)

        for dimensao in DIMENSOES:
            if not indicadores_por_dimensao[dimensao]:
                raise ValueError(
                    f"A dimensão '{dimensao}' ficou sem indicadores classificados."
                )

        chunks_gerais = [
            CHUNKS_CARTA[f"geral_{t}"]
            for t in CHUNKS_GERAIS
            if f"geral_{t}" in CHUNKS_CARTA
        ]

        # Pesquisa web geral: contexto complementar, sem substituir a planilha.
        pesquisa_web = self.llm.pesquisar_contexto_municipio(
            municipio,
            estado=estado,
            codigo_ibge=codigo_ibge,
        )

        analise_geral = self.llm.gerar_analise_geral(
            municipio,
            porte,
            todos_indicadores,
            chunks_gerais,
            dados_contextuais=todos_dados_contextuais,
            pesquisa_web=pesquisa_web,
        )

        relatorio = {"analise_geral": analise_geral, "dimensoes": {}}
        for dimensao, chave in DIMENSAO_PARA_CHAVE.items():
            indicadores = indicadores_por_dimensao[dimensao]

            # Uma validação web pontual por dimensão. O resultado serve apenas
            # para qualificar/atualizar a leitura e evitar recomendações obsoletas.
            pesquisa_web_dimensao = self.llm.pesquisar_validacao_dimensao(
                dimensao=dimensao,
                municipio=municipio,
                indicadores_dimensao=indicadores,
                estado=estado,
                codigo_ibge=codigo_ibge,
            )

            chunks = self.seletor.selecionar(dimensao, indicadores, dados)
            relatorio["dimensoes"][chave] = self.llm.gerar_analise_dimensao(
                dimensao=dimensao,
                municipio=municipio,
                porte=porte,
                indicadores_dimensao=indicadores,
                chunks_selecionados=chunks,
                dados_contextuais_dimensao=dados_contextuais_por_dimensao[dimensao],
                pesquisa_web_dimensao=pesquisa_web_dimensao,
            )

        relatorio["metadados"] = {
            "municipio": municipio,
            "porte": porte,
            "codigo_ibge": codigo_ibge,
            "modelo": self.config.modelo,
            "escala_maturidade": "0-7",
            "pesquisa_web": "Google Search Grounding: geral + validação por dimensão",
            "indicadores_nao_classificados": sorted(
                set(self.classificador.nao_classificados)
            ),
        }
        return relatorio

    def salvar_relatorio(self, municipio: str, relatorio: dict):
        return gerar_relatorio_word(municipio, relatorio, self.config.output_dir)
