"""Clientes Gemini e índices FAISS usados pelo pipeline."""
from __future__ import annotations

import os

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document as LCDocument
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from . import config
from .classificacao import DIMENSOES, PALAVRAS_CHAVE_TOPICO
from .dados_carta import CHUNKS_CARTA


def criar_llm():
    return ChatGoogleGenerativeAI(
        model=config.MODELO,
        google_api_key=config.obter_api_key(),
        temperature=config.CONFIG.temperature,
        top_p=config.CONFIG.top_p,
        max_output_tokens=config.CONFIG.max_output_tokens,
    )


def criar_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model=config.MODELO_EMBEDDING,
        google_api_key=config.obter_api_key(),
    )


def _construir_indice_chunks(embeddings):
    documentos = [
        LCDocument(
            page_content=f"{c['topico']}: {c['texto']}",
            metadata={
                "chunk_id": c["chunk_id"],
                "dimensao": c["dimensao"],
                "topico": c["topico"],
            },
        )
        for c in CHUNKS_CARTA.values()
    ]
    return FAISS.from_documents(documentos, embeddings)


def carregar_ou_construir_indice_chunks(embeddings):
    caminho = str(config.FAISS_INDEX_CHUNKS_PATH)
    if os.path.exists(caminho):
        return FAISS.load_local(
            caminho, embeddings, allow_dangerous_deserialization=True
        )
    indice = _construir_indice_chunks(embeddings)
    indice.save_local(caminho)
    return indice


def _construir_indice_topicos(embeddings):
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
    return FAISS.from_documents(documentos, embeddings)


def carregar_ou_construir_indice_topicos(embeddings):
    caminho = str(config.FAISS_INDEX_TOPICOS_PATH)
    if os.path.exists(caminho):
        return FAISS.load_local(
            caminho, embeddings, allow_dangerous_deserialization=True
        )
    indice = _construir_indice_topicos(embeddings)
    indice.save_local(caminho)
    return indice


def criar_classificador_por_embedding(indice_topicos):
    def classificar_por_embedding(nome_indicador):
        resultados = indice_topicos.similarity_search_with_relevance_scores(
            nome_indicador, k=1
        )
        if not resultados:
            return None
        doc, score = resultados[0]
        if score < config.LIMIAR_RELEVANCIA_TOPICO:
            return None
        return {
            "dimensao": doc.metadata["dimensao"],
            "topico": doc.metadata["topico"],
            "chunk_id": doc.metadata["chunk_id"],
        }

    return classificar_por_embedding
