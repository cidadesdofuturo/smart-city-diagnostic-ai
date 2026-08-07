from __future__ import annotations

from .config import Config
from .dados import CHUNKS_CARTA
from .taxonomia import DIMENSOES, PALAVRAS_CHAVE_TOPICO


class EmbeddingsService:
    """Gerencia embeddings e os dois índices FAISS do notebook-fonte.

    Os imports pesados são tardios para permitir testes da lógica local sem
    chave de API ou instalação do stack de IA.
    """

    def __init__(self, config: Config):
        self.config = config
        self._embeddings = None
        self._indice_topicos = None
        self._indice_chunks = None

    def _deps(self):
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            from langchain_community.vectorstores import FAISS
            from langchain_core.documents import Document as LCDocument
        except ImportError as exc:
            raise RuntimeError(
                "Dependências de IA ausentes. Execute: pip install -r requirements.txt"
            ) from exc
        return GoogleGenerativeAIEmbeddings, FAISS, LCDocument

    @property
    def embeddings(self):
        if self._embeddings is None:
            GoogleGenerativeAIEmbeddings, _, _ = self._deps()
            self._embeddings = GoogleGenerativeAIEmbeddings(
                model=self.config.modelo_embedding,
                google_api_key=self.config.api_key,
            )
        return self._embeddings

    def _construir_indice_topicos(self):
        _, FAISS, LCDocument = self._deps()
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
        return FAISS.from_documents(documentos, self.embeddings)

    def _construir_indice_chunks(self):
        _, FAISS, LCDocument = self._deps()
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
        return FAISS.from_documents(documentos, self.embeddings)

    def indice_topicos(self):
        if self._indice_topicos is None:
            _, FAISS, _ = self._deps()
            path = self.config.caminho_faiss_topicos
            if path.exists():
                self._indice_topicos = FAISS.load_local(
                    str(path), self.embeddings, allow_dangerous_deserialization=True
                )
            else:
                self._indice_topicos = self._construir_indice_topicos()
                self._indice_topicos.save_local(str(path))
        return self._indice_topicos

    def indice_chunks(self):
        if self._indice_chunks is None:
            _, FAISS, _ = self._deps()
            path = self.config.caminho_faiss_chunks
            if path.exists():
                self._indice_chunks = FAISS.load_local(
                    str(path), self.embeddings, allow_dangerous_deserialization=True
                )
            else:
                self._indice_chunks = self._construir_indice_chunks()
                self._indice_chunks.save_local(str(path))
        return self._indice_chunks

    def classificar_topico(self, nome_indicador: str) -> dict | None:
        resultados = self.indice_topicos().similarity_search_with_relevance_scores(
            nome_indicador, k=1
        )
        if not resultados:
            return None
        doc, score = resultados[0]
        if score < self.config.limiar_relevancia_topico:
            return None
        return {
            "dimensao": doc.metadata["dimensao"],
            "topico": doc.metadata["topico"],
            "chunk_id": doc.metadata["chunk_id"],
        }

    def buscar_chunk_na_dimensao(self, consulta: str, dimensao: str):
        resultados = self.indice_chunks().similarity_search(
            consulta,
            k=1,
            filter={"dimensao": dimensao},
            fetch_k=50,
        )
        return resultados[0] if resultados else None
