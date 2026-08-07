"""Índices FAISS usados como fallback semântico no pipeline.

Replica a lógica do notebook: um índice sobre os tópicos serve para classificar
indicadores novos; outro índice sobre os chunks da Carta recupera uma base
conceitual próxima quando um tópico não tem chunk dedicado.
"""
from __future__ import annotations

import os

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document as LCDocument
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from .carta import CartaRepository
from .config import Config
from .data.dimensoes import DIMENSOES, PALAVRAS_CHAVE_TOPICO


class GestorEmbeddings:
    LIMIAR_RELEVANCIA_TOPICO = 0.75

    def __init__(self, config: Config, carta: CartaRepository):
        self._config = config
        self._carta = carta
        self._embeddings = GoogleGenerativeAIEmbeddings(
            model=config.modelo_embedding,
            google_api_key=config.validar_api_key(),
        )
        self._indice_topicos = None
        self._indice_chunks = None

    def _construir_indice_topicos(self):
        documentos = []
        for dimensao, info in DIMENSOES.items():
            for topico in info["topicos"]:
                palavras = PALAVRAS_CHAVE_TOPICO.get(topico, [])
                texto = f"{topico.replace('_', ' ')}: {', '.join(palavras)}"
                documentos.append(
                    LCDocument(
                        page_content=texto,
                        metadata={
                            "dimensao": dimensao,
                            "topico": topico.replace("_", " ").title(),
                            "chunk_id": f"{info['prefixo']}_{topico}",
                        },
                    )
                )
        return FAISS.from_documents(documentos, self._embeddings)

    def indice_topicos(self):
        if self._indice_topicos is not None:
            return self._indice_topicos
        caminho = self._config.caminho_faiss_topicos
        if os.path.exists(caminho):
            self._indice_topicos = FAISS.load_local(
                caminho, self._embeddings, allow_dangerous_deserialization=True
            )
        else:
            self._indice_topicos = self._construir_indice_topicos()
            self._indice_topicos.save_local(caminho)
        return self._indice_topicos

    def _construir_indice_chunks(self):
        documentos = [
            LCDocument(
                page_content=f"{c.topico}: {c.texto}",
                metadata={
                    "chunk_id": c.chunk_id,
                    "dimensao": c.dimensao,
                    "topico": c.topico,
                },
            )
            for c in self._carta.todos()
        ]
        return FAISS.from_documents(documentos, self._embeddings)

    def indice_chunks(self):
        if self._indice_chunks is not None:
            return self._indice_chunks
        caminho = self._config.caminho_faiss_chunks
        if os.path.exists(caminho):
            self._indice_chunks = FAISS.load_local(
                caminho, self._embeddings, allow_dangerous_deserialization=True
            )
        else:
            self._indice_chunks = self._construir_indice_chunks()
            self._indice_chunks.save_local(caminho)
        return self._indice_chunks
