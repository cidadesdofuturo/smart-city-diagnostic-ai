from __future__ import annotations

from .dados import CHUNKS_CARTA
from .maturidade import obter_nivel_indicador
from .taxonomia import CHUNKS_GERAIS, TOPICOS_SEM_CHUNK_NA_CARTA


class SeletorChunks:
    def __init__(self, classificador, embeddings_service):
        self.classificador = classificador
        self.embeddings_service = embeddings_service

    def selecionar(self, dimensao, indicadores_dimensao, linha_planilha=None,
                   usar_fallback_semantico=True):
        chunks_gerais = [
            CHUNKS_CARTA[f"geral_{t}"]
            for t in CHUNKS_GERAIS
            if f"geral_{t}" in CHUNKS_CARTA
        ]

        pior_nivel_por_chunk = {}
        for nome, valor in indicadores_dimensao.items():
            classificacao = self.classificador.classificar(nome)
            if not classificacao or classificacao["dimensao"] != dimensao:
                continue
            nivel = obter_nivel_indicador(nome, valor, linha_planilha)
            chunk_id = classificacao["chunk_id"]
            nivel_efetivo = 99 if nivel is None else nivel
            pior_nivel_por_chunk[chunk_id] = min(
                pior_nivel_por_chunk.get(chunk_id, 99), nivel_efetivo
            )

        topicos_ordenados = sorted(
            pior_nivel_por_chunk, key=lambda cid: pior_nivel_por_chunk[cid]
        )

        chunks_topicos = []
        ids_incluidos = set()
        for cid in topicos_ordenados:
            if cid in CHUNKS_CARTA:
                chunks_topicos.append(CHUNKS_CARTA[cid])
                ids_incluidos.add(cid)
            elif usar_fallback_semantico and cid in TOPICOS_SEM_CHUNK_NA_CARTA:
                nome_topico = cid.split("_", 1)[1].replace("_", " ")
                doc = self.embeddings_service.buscar_chunk_na_dimensao(
                    nome_topico, dimensao
                )
                if doc is not None:
                    encontrado = doc.metadata["chunk_id"]
                    if encontrado not in ids_incluidos:
                        chunks_topicos.append(CHUNKS_CARTA[encontrado])
                        ids_incluidos.add(encontrado)

        return chunks_gerais + chunks_topicos
