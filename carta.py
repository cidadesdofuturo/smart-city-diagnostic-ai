"""Repositório dos chunks temáticos da Carta Brasileira para Cidades
Inteligentes, encapsulado em uma classe (`CartaRepository`) em vez de um
dict global — permite testar com dados alternativos e trata erros de
carregamento explicitamente."""
from __future__ import annotations

import json
from importlib import resources
from typing import Iterable

from .exceptions import CartaError, ChunkNaoEncontradoError
from .models import ChunkCarta


class CartaRepository:
    """Carrega e consulta os chunks pré-extraídos da Carta.

    Uso:
        carta = CartaRepository.carregar_padrao()
        chunk = carta.obter("geral_conceito_brasileiro_de_cidades_inteligentes")
        chunks_gerais = carta.chunks_gerais(["conceito_brasileiro_de_cidades_inteligentes"])
    """

    def __init__(self, chunks: dict[str, ChunkCarta], topicos_sem_chunk: Iterable[str]):
        self._chunks = chunks
        self.topicos_sem_chunk = frozenset(topicos_sem_chunk)

    @classmethod
    def carregar_padrao(cls) -> "CartaRepository":
        """Carrega os chunks e a lista de tópicos sem conteúdo dedicado a
        partir dos arquivos JSON empacotados em `data/`."""
        try:
            chunks_raw = json.loads(
                resources.files("municipio_analise.data").joinpath("carta_chunks.json").read_text(encoding="utf-8")
            )
            topicos_raw = json.loads(
                resources.files("municipio_analise.data").joinpath("topicos_sem_chunk.json").read_text(encoding="utf-8")
            )
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            raise CartaError(f"Falha ao carregar os dados da Carta: {exc}") from exc

        chunks = {
            chunk_id: ChunkCarta(**dados) for chunk_id, dados in chunks_raw.items()
        }
        return cls(chunks=chunks, topicos_sem_chunk=topicos_raw)

    def __len__(self) -> int:
        return len(self._chunks)

    def __contains__(self, chunk_id: str) -> bool:
        return chunk_id in self._chunks

    def obter(self, chunk_id: str) -> ChunkCarta:
        try:
            return self._chunks[chunk_id]
        except KeyError as exc:
            raise ChunkNaoEncontradoError(f"Chunk '{chunk_id}' não encontrado na Carta.") from exc

    def obter_opcional(self, chunk_id: str) -> ChunkCarta | None:
        return self._chunks.get(chunk_id)

    def todos(self) -> list[ChunkCarta]:
        """Retorna todos os chunks na ordem em que foram carregados."""
        return list(self._chunks.values())

    def chunks_gerais(self, topicos_gerais: Iterable[str]) -> list[ChunkCarta]:
        """Retorna os chunks gerais (prefixo 'geral_') existentes, na ordem informada."""
        resultado = []
        for topico in topicos_gerais:
            chunk = self.obter_opcional(f"geral_{topico}")
            if chunk is not None:
                resultado.append(chunk)
        return resultado
