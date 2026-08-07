"""Configuração central do pipeline, alinhada ao notebook de referência."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Config:
    base_path: Path = field(default_factory=lambda: Path(
        os.getenv("MUNICIPIO_DADOS_DIR", "/content/drive/MyDrive/Scripts/Analise de municipio")
    ))
    nome_arquivo_planilha: str = "indicadores.xlsx"
    coluna_municipio: str = "municipio"
    coluna_populacao: str = "populacao total estimada do municipio"
    modelo: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    temperature: float = float(os.getenv("GEMINI_TEMPERATURE", "0.2"))
    top_p: float = float(os.getenv("GEMINI_TOP_P", "0.9"))
    max_output_tokens: int = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "4096"))
    tentativas_llm: int = int(os.getenv("TENTATIVAS_LLM", "2"))
    modelo_embedding: str = os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")
    limiar_relevancia_topico: float = float(os.getenv("LIMIAR_RELEVANCIA_TOPICO", "0.75"))

    @property
    def caminho_planilha(self) -> Path:
        return self.base_path / self.nome_arquivo_planilha

    @property
    def caminho_faiss_topicos(self) -> Path:
        return self.base_path / "faiss_index_topicos"

    @property
    def caminho_faiss_chunks(self) -> Path:
        return self.base_path / "faiss_index_chunks"

    def obter_api_key(self) -> str:
        chave = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not chave:
            raise ValueError(
                "Chave Gemini não configurada. Defina GOOGLE_API_KEY ou GEMINI_API_KEY."
            )
        return chave


CONFIG = Config()

# Compatibilidade simples com os módulos existentes.
BASE_PATH = CONFIG.base_path
ARQUIVO_PLANILHA = CONFIG.caminho_planilha
COLUNA_MUNICIPIO = CONFIG.coluna_municipio
COLUNA_POPULACAO = CONFIG.coluna_populacao
MODELO = CONFIG.modelo
MODELO_EMBEDDING = CONFIG.modelo_embedding
FAISS_INDEX_TOPICOS_PATH = CONFIG.caminho_faiss_topicos
FAISS_INDEX_CHUNKS_PATH = CONFIG.caminho_faiss_chunks
LIMIAR_RELEVANCIA_TOPICO = CONFIG.limiar_relevancia_topico
TENTATIVAS_LLM = CONFIG.tentativas_llm


def obter_api_key() -> str:
    return CONFIG.obter_api_key()


def validar_configuracao() -> None:
    CONFIG.base_path.mkdir(parents=True, exist_ok=True)
    CONFIG.obter_api_key()
