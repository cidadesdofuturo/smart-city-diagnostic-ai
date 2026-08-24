from __future__ import annotations

from .config import Config
from .taxonomia import DIMENSOES, PALAVRAS_CHAVE_TOPICO


class EmbeddingsService:
    """Gemini é usado somente para embeddings/FAISS.

    Dependências pesadas são carregadas sob demanda, permitindo importar e
    testar o restante do pacote sem inicializar clientes externos.
    """

    def __init__(self, config: Config):
        self.config = config
        self._embeddings = None
        self._indice_topicos = None
        self._indice_chunks = None

    @property
    def embeddings(self):
        if self._embeddings is None:
            self.config.validar(exigir_planilha=False, exigir_api=False, exigir_embeddings=True)
            try:
                from langchain_google_genai import GoogleGenerativeAIEmbeddings
            except ImportError as exc:
                raise RuntimeError(
                    "Instale as dependências do projeto (langchain-google-genai)."
                ) from exc
            self._embeddings = GoogleGenerativeAIEmbeddings(
                model=self.config.modelo_embedding,
                google_api_key=self.config.gemini_api_key,
            )
        return self._embeddings

    def _docs_topicos(self):
        try:
            from langchain_core.documents import Document as LCDocument
        except ImportError as exc:
            raise RuntimeError("Instale langchain-core.") from exc
        docs = []
        for dimensao, info in DIMENSOES.items():
            for topico in info["topicos"]:
                termos = PALAVRAS_CHAVE_TOPICO.get(topico, [])
                docs.append(LCDocument(
                    page_content=(
                        f"Dimensão: {dimensao}. Tópico: {topico.replace('_', ' ')}. "
                        f"Termos relacionados: {', '.join(termos)}"
                    ),
                    metadata={
                        "dimensao": dimensao,
                        "topico": topico.replace("_", " ").title(),
                        "chunk_id": f"{info['prefixo']}_{topico}",
                    },
                ))
        return docs

    @property
    def indice_topicos(self):
        if self._indice_topicos is not None:
            return self._indice_topicos
        try:
            from langchain_community.vectorstores import FAISS
        except ImportError as exc:
            raise RuntimeError("Instale langchain-community e faiss-cpu.") from exc
        caminho = self.config.caminho_faiss_topicos
        if caminho.exists():
            self._indice_topicos = FAISS.load_local(
                str(caminho), self.embeddings, allow_dangerous_deserialization=True
            )
        else:
            self._indice_topicos = FAISS.from_documents(self._docs_topicos(), self.embeddings)
            caminho.parent.mkdir(parents=True, exist_ok=True)
            self._indice_topicos.save_local(str(caminho))
        return self._indice_topicos

    def classificar_topico(self, nome_indicador: str):
        resultados = self.indice_topicos.similarity_search_with_score(nome_indicador, k=1)
        if not resultados:
            return None
        doc, distancia = resultados[0]
        score = 1.0 / (1.0 + max(0.0, float(distancia)))
        if score < self.config.limiar_relevancia_topico:
            return None
        return dict(doc.metadata)

    @property
    def indice_chunks(self):
        if self._indice_chunks is not None:
            return self._indice_chunks
        from .dados import CHUNKS_CARTA
        try:
            from langchain_core.documents import Document as LCDocument
            from langchain_community.vectorstores import FAISS
        except ImportError as exc:
            raise RuntimeError("Instale langchain-core, langchain-community e faiss-cpu.") from exc
        caminho = self.config.caminho_faiss_chunks
        if caminho.exists():
            self._indice_chunks = FAISS.load_local(
                str(caminho), self.embeddings, allow_dangerous_deserialization=True
            )
        else:
            docs = [
                LCDocument(
                    page_content=c["texto"],
                    metadata={"chunk_id": cid, "dimensao": c.get("dimensao", "")},
                )
                for cid, c in CHUNKS_CARTA.items()
            ]
            self._indice_chunks = FAISS.from_documents(docs, self.embeddings)
            caminho.parent.mkdir(parents=True, exist_ok=True)
            self._indice_chunks.save_local(str(caminho))
        return self._indice_chunks
