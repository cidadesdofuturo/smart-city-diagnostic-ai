from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    """Configuração central do pipeline.

    O notebook-fonte usa Gemini 3.6 Flash e escala de maturidade 0–7.
    A chave nunca é gravada no repositório: use GOOGLE_API_KEY (preferido)
    ou GEMINI_API_KEY no ambiente.
    """

    base_path: Path | str = field(
        default_factory=lambda: Path(os.getenv("MUNICIPIO_DADOS_DIR", "./dados"))
    )
    planilha_nome: str = "indicadores.xlsx"
    coluna_municipio: str = "municipio"
    coluna_populacao: str = "populacao total estimada do municipio"
    modelo: str = "gemini-3.6-flash"
    modelo_embedding: str = "models/gemini-embedding-001"
    max_output_tokens: int = 4096
    limiar_relevancia_topico: float = 0.75
    tentativas_llm: int = 2
    api_key: str | None = None
    faiss_topicos_nome: str = "faiss_index_topicos"
    faiss_chunks_nome: str = "faiss_index_chunks"

    def __post_init__(self):
        self.base_path = Path(self.base_path)
        if self.api_key is None:
            self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

    @property
    def caminho_planilha(self) -> Path:
        return self.base_path / self.planilha_nome

    @property
    def caminho_faiss_topicos(self) -> Path:
        return self.base_path / self.faiss_topicos_nome

    @property
    def caminho_faiss_chunks(self) -> Path:
        return self.base_path / self.faiss_chunks_nome

    @property
    def output_dir(self) -> Path:
        return self.base_path

    def validar(self, *, exigir_planilha: bool = True, exigir_api: bool = True) -> None:
        self.base_path.mkdir(parents=True, exist_ok=True)
        if exigir_api and not self.api_key:
            raise ValueError(
                "Chave da API não configurada. Defina GOOGLE_API_KEY ou GEMINI_API_KEY."
            )
        if exigir_planilha and not self.caminho_planilha.exists():
            raise FileNotFoundError(
                f"Planilha de indicadores não encontrada: {self.caminho_planilha}"
            )
