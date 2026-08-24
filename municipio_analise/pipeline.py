from __future__ import annotations

import time

from .classificador import ClassificadorIndicadores
from .config import Config
from .contexto import obter_dados_contextuais
from .embeddings_service import EmbeddingsService
from .llm_service import LLMService, normalizar_codigo_ibge
from .planilha import carregar_planilha, obter_linha_municipio
from .relatorio import gerar_relatorio_word
from .seletor_chunks import SeletorChunks
from .taxonomia import DIMENSOES, DIMENSAO_PARA_CHAVE
from .utils import classificar_porte


class PipelineAnaliseMunicipio:
    def __init__(self, config: Config | None = None, *, llm_service=None, seletor_chunks=None):
        self.config = config or Config()
        self.embeddings = EmbeddingsService(self.config)
        self.classificador = ClassificadorIndicadores(self.embeddings)
        self.seletor = seletor_chunks or SeletorChunks(self.classificador, self.embeddings, self.config)
        self._llm = llm_service

    @property
    def llm(self):
        if self._llm is None:
            self._llm = LLMService(self.config)
        return self._llm

    def analisar(self, municipio: str, *, gerar_word: bool = True):
        df = carregar_planilha(self.config)
        dados = obter_linha_municipio(df, self.config.coluna_municipio, municipio)
        populacao = int(dados[self.config.coluna_populacao])
        porte = classificar_porte(populacao)
        estado = dados.get("estado", None)
        codigo_ibge = normalizar_codigo_ibge(dados.get("cod municipio", None))

        ignoradas = {self.config.coluna_municipio, self.config.coluna_populacao, "cod municipio", "estado", "avaliada"}
        candidatos = dados.drop(labels=[c for c in ignoradas if c in dados.index]).to_dict()
        indicadores_por_dimensao = {d: {} for d in DIMENSOES}
        for nome, valor in candidatos.items():
            clas = self.classificador.classificar(nome)
            if clas:
                indicadores_por_dimensao[clas["dimensao"]][nome] = valor

        relatorio = {"analise_geral": "", "dimensoes": {}, "metadata": {}}

        # Fonte de verdade do notebook: rascunho SEM web -> validação -> revisão.
        for indice, (dimensao, chave) in enumerate(DIMENSAO_PARA_CHAVE.items()):
            indicadores = indicadores_por_dimensao[dimensao]
            if not indicadores:
                raise ValueError(f"Dimensão '{dimensao}' ficou sem indicadores classificados.")
            dados_contextuais = obter_dados_contextuais(dimensao, dados)
            chunks = self.seletor.selecionar(dimensao, indicadores, linha_planilha=dados)
            rascunho = self.llm.gerar_analise_dimensao(
                dimensao, municipio, porte, indicadores, chunks,
                dados_contextuais_dimensao=dados_contextuais,
            )
            validacao = self.llm.pesquisar_validacao_dimensao(
                dimensao, municipio, indicadores, rascunho,
                estado=estado, codigo_ibge=codigo_ibge,
            )
            relatorio["dimensoes"][chave] = self.llm.revisar_analise_dimensao(
                dimensao, municipio, porte, indicadores, rascunho,
                dados_contextuais_dimensao=dados_contextuais,
                validacao_web=validacao,
            )
            if indice < len(DIMENSAO_PARA_CHAVE) - 1 and self.config.pausa_entre_pesquisas_web:
                time.sleep(self.config.pausa_entre_pesquisas_web)

        # Análise Geral somente após as quatro dimensões finais; sem nova web.
        relatorio["analise_geral"] = self.llm.gerar_analise_geral(
            municipio, porte, relatorio["dimensoes"]
        )
        relatorio["metadata"] = {
            "modelo": self.config.modelo,
            "modelo_embedding": self.config.modelo_embedding,
            "web_search": "Claude Web Search: validação pós-rascunho de até 5 pontos por dimensão",
            "rag_carta": self.config.modo_rag_carta,
            "pipeline_carta": self.config.versao_pipeline_carta_completa,
            "codigo_ibge": codigo_ibge,
            "porte": porte,
            "indicadores_nao_classificados": sorted(set(self.classificador.indicadores_nao_classificados)),
        }
        if gerar_word:
            relatorio["arquivo_word"] = str(gerar_relatorio_word(municipio, relatorio, self.config.output_dir))
        return relatorio

    # Alias de compatibilidade.
    executar = analisar
