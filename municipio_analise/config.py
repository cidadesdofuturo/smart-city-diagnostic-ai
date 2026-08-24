from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    """Configuração central do pipeline modular.

    Sincronizada com o notebook de referência de 18/08/2026:
    - Claude Sonnet 4.6 para geração e revisão;
    - Claude Web Search para validação pós-rascunho;
    - Gemini apenas para embeddings/FAISS;
    - escala de maturidade 0–7;
    - RAG granular da Carta revisada.
    """

    base_path: Path | str = field(
        default_factory=lambda: Path(os.getenv("MUNICIPIO_DADOS_DIR", "./dados"))
    )
    planilha_nome: str = "indicadores.xlsx"
    coluna_municipio: str = "municipio"
    coluna_populacao: str = "populacao total estimada do municipio"

    modelo: str = "claude-sonnet-4-6"
    modelo_pesquisa_web: str = "claude-sonnet-4-6"
    modelo_embedding: str = "models/gemini-embedding-001"
    max_output_tokens: int = 4096

    tentativas_llm: int = 2
    pausa_entre_pesquisas_web: int = 10
    max_usos_web_por_dimensao: int = 5

    limiar_relevancia_topico: float = 0.75

    modo_rag_carta: str = "completa"
    max_indicadores_rag_por_dimensao: int = 5
    k_candidatos_rag_por_indicador: int = 8
    max_chunks_carta_completa: int = 8
    peso_maximo_maturidade_rag: float = 0.30
    bonus_dimensao_rag: float = 0.05
    bonus_topico_rag: float = 0.04
    bonus_cobertura_multipla_rag: float = 0.02
    limiar_semantico_carta_completa: float | None = None
    auditar_rag_carta_completa: bool = True
    versao_pipeline_carta_completa: str = "carta-revisada-posicional-v1"

    lote_embedding_carta_completa: int = 45
    pausa_entre_lotes_embedding: int = 65
    max_tentativas_lote_embedding: int = 4

    faiss_topicos_nome: str = "faiss_index_topicos"
    faiss_chunks_nome: str = "faiss_index_chunks"
    faiss_carta_completa_nome: str = "faiss_carta_completa_v1"
    faiss_carta_manifest_nome: str = "faiss_carta_completa_v1_manifest.json"

    anthropic_api_key: str | None = None
    gemini_api_key: str | None = None

    # Compatibilidade com código/testes antigos que passavam Config(api_key=...).
    # Para uso real, prefira as duas chaves separadas acima.
    api_key: str | None = None

    ancoras_deterministicas_carta: dict[str, list[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.base_path = Path(self.base_path)

        if self.anthropic_api_key is None:
            self.anthropic_api_key = (
                os.getenv("ANTHROPIC_API_KEY")
                or self.api_key
            )

        if self.gemini_api_key is None:
            self.gemini_api_key = (
                os.getenv("GEMINI_API_KEY")
                or os.getenv("GOOGLE_API_KEY")
                or os.getenv("API")
                or self.api_key
            )

        # Mantém o atributo legado apontando para a chave do LLM principal.
        if self.api_key is None:
            self.api_key = self.anthropic_api_key

        if self.modo_rag_carta not in {"completa", "antigo"}:
            raise ValueError("modo_rag_carta deve ser 'completa' ou 'antigo'.")

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
    def caminho_faiss_carta_completa(self) -> Path:
        return self.base_path / self.faiss_carta_completa_nome

    @property
    def caminho_manifesto_carta_completa(self) -> Path:
        return self.base_path / self.faiss_carta_manifest_nome

    @property
    def output_dir(self) -> Path:
        return self.base_path

    def validar(
        self,
        *,
        exigir_planilha: bool = True,
        exigir_api: bool = True,
        exigir_embeddings: bool | None = None,
    ) -> None:
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Compatibilidade: nas versões antigas, exigir_api=False desabilitava toda validação de chave.
        if exigir_embeddings is None:
            exigir_embeddings = exigir_api

        if exigir_api and not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY não configurada. "
                "Ela é necessária para geração, revisão e Claude Web Search."
            )

        if exigir_embeddings and not self.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY/GOOGLE_API_KEY não configurada. "
                "Ela é necessária para embeddings e FAISS."
            )

        if exigir_planilha and not self.caminho_planilha.exists():
            raise FileNotFoundError(
                f"Planilha de indicadores não encontrada: {self.caminho_planilha}"
            )
