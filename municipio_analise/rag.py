# =====================================================
# CLIENTES DE MODELO E ÍNDICES FAISS (busca semântica / RAG)
# =====================================================
"""Configura o LLM, os embeddings e os dois índices FAISS usados no
projeto:

- índice de chunks da Carta: usado como fallback para os tópicos listados
  em dados_carta.TOPICOS_SEM_CHUNK_NA_CARTA, que hoje ficam sem nenhum
  trecho de referência direto (ver classificacao.selecionar_chunks_dimensao);
- índice de tópicos: usado por classificacao.classificar_indicador quando
  um indicador não bate por nome exato nem por palavra-chave.

Os índices são persistidos localmente (config.FAISS_INDEX_*_PATH): gerados
uma única vez e reaproveitados nas próximas execuções, para evitar o
custo/tempo de reprocessar embeddings sempre.
"""

import os

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document as LCDocument

from . import config
from .classificacao import DIMENSOES, PALAVRAS_CHAVE_TOPICO
from .dados_carta import CHUNKS_CARTA


def criar_llm():
    return ChatGoogleGenerativeAI(
        model=config.MODELO,
        google_api_key=config.GOOGLE_API_KEY,
        temperature=0.4,
        top_p=0.9,
        max_output_tokens=4096,
    )


def criar_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model=config.MODELO_EMBEDDING,
        google_api_key=config.GOOGLE_API_KEY,
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
        return FAISS.load_local(caminho, embeddings, allow_dangerous_deserialization=True)
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
        return FAISS.load_local(caminho, embeddings, allow_dangerous_deserialization=True)
    indice = _construir_indice_topicos(embeddings)
    indice.save_local(caminho)
    return indice


def criar_classificador_por_embedding(indice_topicos):
    """Retorna uma função que classifica o nome de um indicador por
    similaridade semântica ao tópico mais próximo (fallback semântico de
    classificacao.classificar_indicador), ou None se a melhor
    correspondência ficar abaixo de config.LIMIAR_RELEVANCIA_TOPICO."""

    def classificar_por_embedding(nome_indicador):
        resultados = indice_topicos.similarity_search_with_relevance_scores(nome_indicador, k=1)
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
