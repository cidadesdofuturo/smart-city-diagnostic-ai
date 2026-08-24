from __future__ import annotations

from .carta_granular import CartaGranularService
from .config import Config
from .dados import CHUNKS_CARTA, TOPICOS_SEM_CHUNK_NA_CARTA
from .maturidade import obter_nivel_indicador
from .taxonomia import CHUNKS_GERAIS
from .utils import normalizar_texto


class SeletorChunks:
    def __init__(self, classificador, embeddings_service, config: Config | None = None):
        self.classificador = classificador
        self.embeddings = embeddings_service
        self.config = config or embeddings_service.config
        self.carta = CartaGranularService(self.config, embeddings_service)

    def _antigo(self, dimensao, indicadores_dimensao, linha_planilha=None, usar_fallback_semantico=True):
        chunks_gerais = [
            CHUNKS_CARTA[f"geral_{t}"] for t in CHUNKS_GERAIS if f"geral_{t}" in CHUNKS_CARTA
        ]
        pior_nivel_por_chunk = {}
        for nome, valor in indicadores_dimensao.items():
            classificacao = self.classificador.classificar(nome)
            if not classificacao or classificacao["dimensao"] != dimensao:
                continue
            nivel = obter_nivel_indicador(nome, valor, linha_planilha)
            cid = classificacao["chunk_id"]
            efetivo = 99 if nivel is None else nivel
            pior_nivel_por_chunk[cid] = min(pior_nivel_por_chunk.get(cid, 99), efetivo)
        chunks_topicos, incluidos = [], set()
        for cid in sorted(pior_nivel_por_chunk, key=lambda c: pior_nivel_por_chunk[c]):
            if cid in CHUNKS_CARTA:
                chunks_topicos.append(CHUNKS_CARTA[cid]); incluidos.add(cid)
            elif usar_fallback_semantico and cid in TOPICOS_SEM_CHUNK_NA_CARTA:
                nome_topico = cid.split("_", 1)[1].replace("_", " ")
                resultados = self.embeddings.indice_chunks.similarity_search(
                    nome_topico, k=1, filter={"dimensao": dimensao}, fetch_k=50
                )
                for doc in resultados:
                    achado = doc.metadata["chunk_id"]
                    if achado not in incluidos:
                        chunks_topicos.append(CHUNKS_CARTA[achado]); incluidos.add(achado)
        return chunks_gerais + chunks_topicos

    def _peso_maturidade(self, nivel):
        if nivel is None:
            return 1.0
        nivel = max(0.0, min(7.0, float(nivel)))
        return 1.0 + self.config.peso_maximo_maturidade_rag * ((7.0 - nivel) / 7.0)

    @staticmethod
    def _score_semantico(distancia):
        try:
            distancia = max(0.0, float(distancia))
        except Exception:
            return 0.0
        return 1.0 / (1.0 + distancia)

    def _prioridades(self, dimensao, indicadores_dimensao, linha_planilha=None):
        melhores = {}
        for nome, valor in indicadores_dimensao.items():
            clas = self.classificador.classificar(nome)
            if not clas or clas["dimensao"] != dimensao:
                continue
            nivel = obter_nivel_indicador(nome, valor, linha_planilha)
            topico = clas["topico"]
            ordem = 99 if nivel is None else float(nivel)
            reg = {"indicador": nome, "valor": valor, "nivel": nivel, "topico": topico, "nivel_ordenacao": ordem}
            atual = melhores.get(topico)
            if atual is None or ordem < atual["nivel_ordenacao"]:
                melhores[topico] = reg
        ordenados = sorted(
            melhores.values(),
            key=lambda x: (x["nivel_ordenacao"], normalizar_texto(x["topico"]), normalizar_texto(x["indicador"])),
        )
        return ordenados[:self.config.max_indicadores_rag_por_dimensao]

    @staticmethod
    def _aderencia_topico(topico_indicador, metadata):
        alvo = normalizar_texto(topico_indicador)
        for topico_meta in metadata.get("topicos_relacionados", []) or []:
            meta = normalizar_texto(str(topico_meta).replace("_", " "))
            if alvo == meta or alvo in meta or meta in alvo:
                return True
        return False

    def _completa(self, dimensao, indicadores_dimensao, linha_planilha=None):
        prioridades = self._prioridades(dimensao, indicadores_dimensao, linha_planilha)
        if not prioridades:
            return []
        candidatos = {}
        for prioridade in prioridades:
            nome, valor, nivel, topico = (
                prioridade["indicador"], prioridade["valor"], prioridade["nivel"], prioridade["topico"]
            )
            query = (
                f"Dimensão municipal: {dimensao}. Tópico: {topico}. "
                f"Indicador prioritário: {nome}. Situação observada no município: {valor}. "
                "Recupere da Carta Brasileira para Cidades Inteligentes os conceitos, diretrizes "
                "e recomendações mais úteis para interpretar esta capacidade ou lacuna municipal."
            )
            resultados = self.carta.indice.similarity_search_with_score(
                query, k=self.config.k_candidatos_rag_por_indicador
            )
            peso = self._peso_maturidade(nivel)
            for doc, distancia in resultados:
                sem = self._score_semantico(distancia)
                if self.config.limiar_semantico_carta_completa is not None and sem < self.config.limiar_semantico_carta_completa:
                    continue
                md = doc.metadata
                cid = md["chunk_id"]
                score = sem * peso
                if dimensao in (md.get("dimensoes", []) or []):
                    score += self.config.bonus_dimensao_rag
                if self._aderencia_topico(topico, md):
                    score += self.config.bonus_topico_rag
                reg = candidatos.setdefault(cid, {
                    "doc": doc, "score_base_max": score, "score_semantico_max": sem,
                    "distancia_min": float(distancia), "indicadores": set(), "topicos_origem": set(),
                })
                reg["score_base_max"] = max(reg["score_base_max"], score)
                reg["score_semantico_max"] = max(reg["score_semantico_max"], sem)
                reg["distancia_min"] = min(reg["distancia_min"], float(distancia))
                reg["indicadores"].add(nome); reg["topicos_origem"].add(topico)

        # Poucas âncoras manuais, somente se configuradas.
        if self.config.ancoras_deterministicas_carta:
            try:
                from langchain_core.documents import Document as LCDocument
            except ImportError as exc:
                raise RuntimeError("Instale langchain-core.") from exc
            for prioridade in prioridades:
                nome = prioridade["indicador"]
                for rec_id in self.config.ancoras_deterministicas_carta.get(nome, []):
                    chunk = self.carta.por_recomendacao.get(rec_id)
                    if not chunk:
                        continue
                    md = {
                        "chunk_id": chunk["chunk_id"], "tipo": chunk["tipo"], "topico": chunk["topico"],
                        "dimensoes": chunk["dimensoes"], "topicos_relacionados": chunk["topicos_relacionados"],
                        "objetivo": chunk["objetivo"], "recomendacao_id": chunk["recomendacao_id"],
                        "pagina_inicio": chunk["pagina_inicio"], "pagina_fim": chunk["pagina_fim"],
                        "publicos": chunk["publicos"], "fonte": "Carta Brasileira para Cidades Inteligentes — Edição Revisada",
                    }
                    candidatos[chunk["chunk_id"]] = {
                        "doc": LCDocument(page_content=chunk["texto"], metadata=md),
                        "score_base_max": 10.0, "score_semantico_max": 1.0, "distancia_min": 0.0,
                        "indicadores": {nome}, "topicos_origem": {prioridade["topico"]},
                    }

        ranking = []
        for cid, reg in candidatos.items():
            extra = max(0, len(reg["indicadores"]) - 1)
            bonus = min(0.08, self.config.bonus_cobertura_multipla_rag * extra)
            reg["score_final"] = reg["score_base_max"] + bonus
            ranking.append((cid, reg))
        ranking.sort(key=lambda item: (-item[1]["score_final"], item[0]))
        selecionados = ranking[:self.config.max_chunks_carta_completa]
        if self.config.auditar_rag_carta_completa:
            print(f"\n📚 RAG Carta completa — {dimensao}: {len(selecionados)} chunk(s).")
            for pos, (cid, reg) in enumerate(selecionados, 1):
                md = reg["doc"].metadata
                print(f"  {pos}. {cid} | rec={md.get('recomendacao_id') or '-'} | score={reg['score_final']:.4f}")
        saida = []
        for cid, _ in selecionados:
            original = self.carta.por_chunk_id.get(cid)
            if original:
                bloco = dict(original); bloco["dimensao_contexto"] = dimensao; saida.append(bloco)
        return saida

    def selecionar(self, dimensao, indicadores_dimensao, linha_planilha=None, usar_fallback_semantico=True):
        if self.config.modo_rag_carta == "completa":
            novos = self._completa(dimensao, indicadores_dimensao, linha_planilha)
            if novos:
                return novos
            print(f"⚠️ RAG granular sem chunks para '{dimensao}'; usando fallback antigo.")
        return self._antigo(dimensao, indicadores_dimensao, linha_planilha, usar_fallback_semantico)
