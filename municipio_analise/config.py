"""Configuração centralizada do pipeline de análise municipal."""
from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Config:
    """Configuração de execução do pipeline de análise municipal."""

    base_path: str = "/content/drive/MyDrive/Scripts/Analise de municipio"
    nome_arquivo_planilha: str = "indicadores.xlsx"

    coluna_municipio: str = "municipio"
    coluna_populacao: str = "populacao total estimada do municipio"
    colunas_ignoradas_analise: tuple[str, ...] = (
        "municipio",
        "populacao total estimada do municipio",
        "cod municipio",
        "estado",
        "avaliada",
    )

    modelo: str = "gemini-2.5-flash"
    temperature: float = 0.2
    top_p: float = 0.9
    max_output_tokens: int = 4096
    tentativas_llm: int = 2

    modelo_embedding: str = "models/gemini-embedding-001"
    nome_faiss_topicos: str = "faiss_index_topicos"
    nome_faiss_chunks: str = "faiss_index_chunks"
    usar_embeddings_semanticos: bool = True

    api_key_env_var: str = "GOOGLE_API_KEY"
    api_key: str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.api_key is None:
            self.api_key = os.environ.get(self.api_key_env_var)

    @property
    def caminho_planilha(self) -> str:
        return f"{self.base_path}/{self.nome_arquivo_planilha}"

    @property
    def caminho_faiss_topicos(self) -> str:
        return f"{self.base_path}/{self.nome_faiss_topicos}"

    @property
    def caminho_faiss_chunks(self) -> str:
        return f"{self.base_path}/{self.nome_faiss_chunks}"

    def caminho_relatorio(self, municipio: str) -> str:
        nome_seguro = municipio.replace(" ", "_")
        return f"{self.base_path}/Relatorio_{nome_seguro}.docx"

    def validar_api_key(self) -> str:
        if not self.api_key:
            raise ValueError(
                f"Nenhuma chave de API encontrada. Defina a variável de "
                f"ambiente {self.api_key_env_var} ou passe api_key= ao criar o Config."
            )
        return self.api_key
