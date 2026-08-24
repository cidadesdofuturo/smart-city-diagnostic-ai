from __future__ import annotations

import hashlib
import json
import re
import time
from collections import defaultdict

from .config import Config
from .dados import CARTA_REVISADA_SNAPSHOT
from .taxonomia import DIMENSOES, PALAVRAS_CHAVE_TOPICO
from .utils import normalizar_texto

OBJETIVO_PRIOR_DIMENSOES = {
    1: list(DIMENSOES.keys()),
    2: ["Econômica", "Sociocultural"],
    3: ["Capacidades Institucionais"],
    4: ["Capacidades Institucionais"],
    5: ["Econômica"],
    6: ["Econômica", "Capacidades Institucionais"],
    7: ["Sociocultural", "Capacidades Institucionais"],
    8: ["Capacidades Institucionais"],
}


def _classificar_metadados_carta(texto, objetivo=None):
    texto_norm = normalizar_texto(texto)
    scores_topicos = {}
    topico_para_dimensao = {}
    for dimensao, info in DIMENSOES.items():
        for topico in info["topicos"]:
            topico_para_dimensao[topico] = dimensao
            termos = [topico.replace("_", " ")] + PALAVRAS_CHAVE_TOPICO.get(topico, [])
            score = 0.0
            for termo in termos:
                termo_norm = normalizar_texto(termo)
                if termo_norm and termo_norm in texto_norm:
                    score += 1.25 if " " in termo_norm else 1.0
            if score > 0:
                scores_topicos[topico] = score
    scores_dimensoes = defaultdict(float)
    for topico, score in scores_topicos.items():
        scores_dimensoes[topico_para_dimensao[topico]] += score
    if objetivo in OBJETIVO_PRIOR_DIMENSOES:
        for dimensao in OBJETIVO_PRIOR_DIMENSOES[objetivo]:
            scores_dimensoes[dimensao] += 0.75
    dimensoes_ordenadas = [
        d for d, s in sorted(scores_dimensoes.items(), key=lambda x: (-x[1], x[0])) if s > 0
    ] or list(DIMENSOES.keys())
    topicos_ordenados = [
        t for t, _ in sorted(scores_topicos.items(), key=lambda x: (-x[1], x[0]))
    ][:3]
    return dimensoes_ordenadas[:3], topicos_ordenados


def _resumir_contexto_objetivo(texto, limite=700):
    texto = re.sub(r"\s+", " ", str(texto)).strip()
    if len(texto) <= limite:
        return texto
    corte = texto[:limite]
    ultimo_ponto = corte.rfind(".")
    if ultimo_ponto >= int(limite * 0.55):
        return corte[:ultimo_ponto + 1]
    return corte.rstrip() + "…"


def _titulo_e_corpo_recomendacao(texto):
    if ":" in texto:
        titulo, corpo = texto.split(":", 1)
        return titulo.strip(), corpo.strip()
    return texto.strip(), ""


def _pai_recomendacao(rec_id):
    partes = rec_id.split(".")
    return None if len(partes) <= 2 else ".".join(partes[:-1])


def preparar_documentos_carta(snapshot=None):
    snapshot = snapshot or CARTA_REVISADA_SNAPSHOT
    objetivos = {int(k): v for k, v in snapshot["objetivos"].items()}
    recs = snapshot["recomendacoes"]
    titulos = {}
    for r in recs:
        titulo, _ = _titulo_e_corpo_recomendacao(r["texto"])
        titulos[r["recomendacao_id"]] = titulo
    documentos = []
    for item in snapshot["conceitos"]:
        dims, tops = _classificar_metadados_carta(item["texto"])
        documentos.append({
            "chunk_id": item["doc_id"], "tipo": "conceito", "topico": item["titulo"],
            "texto": item["texto"], "dimensoes": dims, "topicos_relacionados": tops,
            "objetivo": None, "recomendacao_id": None,
            "pagina_inicio": item["pagina_inicio"], "pagina_fim": item["pagina_fim"],
            "publicos": [],
        })
    for i, item in enumerate(snapshot["principios"], 1):
        texto = f"{item['titulo']}: {item['texto']}"
        dims, tops = _classificar_metadados_carta(texto)
        documentos.append({
            "chunk_id": f"principio_{i}", "tipo": "principio", "topico": item["titulo"].title(),
            "texto": texto, "dimensoes": dims, "topicos_relacionados": tops,
            "objetivo": None, "recomendacao_id": None,
            "pagina_inicio": item["pagina"], "pagina_fim": item["pagina"], "publicos": [],
        })
    for i, item in enumerate(snapshot["diretrizes"], 1):
        texto = f"{item['titulo']}: {item['texto']}"
        dims, tops = _classificar_metadados_carta(texto)
        documentos.append({
            "chunk_id": f"diretriz_{i}", "tipo": "diretriz", "topico": item["titulo"].title(),
            "texto": texto, "dimensoes": dims, "topicos_relacionados": tops,
            "objetivo": None, "recomendacao_id": None,
            "pagina_inicio": item["pagina"], "pagina_fim": item["pagina"], "publicos": [],
        })
    for numero in range(1, 9):
        obj = objetivos[numero]
        texto = f"Objetivo Estratégico {numero}: {obj['titulo']}\nContexto: {obj['contexto']}"
        dims, tops = _classificar_metadados_carta(texto, objetivo=numero)
        documentos.append({
            "chunk_id": f"objetivo_{numero}_contexto", "tipo": "contexto_objetivo",
            "topico": f"Objetivo Estratégico {numero} — {obj['titulo']}", "texto": texto,
            "dimensoes": dims, "topicos_relacionados": tops, "objetivo": numero,
            "recomendacao_id": None, "pagina_inicio": obj["pagina_inicio"],
            "pagina_fim": obj["pagina_fim"], "publicos": [],
        })
    for rec in recs:
        numero_obj = int(rec["objetivo"])
        obj = objetivos[numero_obj]
        rec_id = rec["recomendacao_id"]
        titulo, corpo = _titulo_e_corpo_recomendacao(rec["texto"])
        pai_id = _pai_recomendacao(rec_id)
        pai_txt = f"\nSeção superior {pai_id}: {titulos[pai_id]}" if pai_id and pai_id in titulos else ""
        subtemas = []
        profundidade = len(rec_id.split("."))
        prefixo = rec_id + "."
        for outro_id, outro_titulo in titulos.items():
            if outro_id.startswith(prefixo) and len(outro_id.split(".")) == profundidade + 1:
                subtemas.append(f"{outro_id} {outro_titulo}")
        subtemas_txt = "\nSubtemas: " + "; ".join(subtemas[:8]) if len(corpo) < 120 and subtemas else ""
        contexto_curto = _resumir_contexto_objetivo(obj["contexto"])
        texto_indexacao = (
            f"Objetivo Estratégico {numero_obj}: {obj['titulo']}\n"
            f"Contexto do objetivo: {contexto_curto}{pai_txt}\n"
            f"Recomendação {rec_id}: {rec['texto']}{subtemas_txt}"
        )
        dims, tops = _classificar_metadados_carta(f"{titulo}. {corpo}. {obj['titulo']}", objetivo=numero_obj)
        documentos.append({
            "chunk_id": "rec_" + rec_id.replace(".", "_"), "tipo": "recomendacao",
            "topico": f"Recomendação {rec_id} — {titulo}", "texto": texto_indexacao,
            "dimensoes": dims, "topicos_relacionados": tops, "objetivo": numero_obj,
            "recomendacao_id": rec_id, "pagina_inicio": rec["pagina_inicio"],
            "pagina_fim": rec["pagina_fim"], "publicos": rec.get("publicos", []),
        })
    return documentos


class CartaGranularService:
    def __init__(self, config: Config, embeddings_service):
        self.config = config
        self.embeddings_service = embeddings_service
        self.documentos = preparar_documentos_carta()
        self.por_chunk_id = {c["chunk_id"]: c for c in self.documentos}
        self.por_recomendacao = {
            c["recomendacao_id"]: c for c in self.documentos if c.get("recomendacao_id")
        }
        self._indice = None

    def _documentos_para_lc(self):
        try:
            from langchain_core.documents import Document as LCDocument
        except ImportError as exc:
            raise RuntimeError("Instale langchain-core.") from exc
        return [
            LCDocument(page_content=c["texto"], metadata={
                "chunk_id": c["chunk_id"], "tipo": c["tipo"], "topico": c["topico"],
                "dimensoes": c["dimensoes"], "topicos_relacionados": c["topicos_relacionados"],
                "objetivo": c["objetivo"] if c["objetivo"] is not None else -1,
                "recomendacao_id": c["recomendacao_id"] or "",
                "pagina_inicio": int(c["pagina_inicio"]), "pagina_fim": int(c["pagina_fim"]),
                "publicos": c["publicos"],
                "fonte": "Carta Brasileira para Cidades Inteligentes — Edição Revisada",
            }) for c in self.documentos
        ]

    def _hash(self):
        payload = json.dumps({
            "pipeline": self.config.versao_pipeline_carta_completa,
            "embedding": self.config.modelo_embedding,
            "documentos": self.documentos,
        }, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _ler_manifesto(self):
        p = self.config.caminho_manifesto_carta_completa
        if not p.exists():
            return {}
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _salvar_manifesto(self, total, processados, completo):
        p = self.config.caminho_manifesto_carta_completa
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({
            "hash_documentos": self._hash(),
            "modelo_embedding": self.config.modelo_embedding,
            "pipeline": self.config.versao_pipeline_carta_completa,
            "total_documentos": total,
            "documentos_embutidos": processados,
            "completo": bool(completo),
            "total_recomendacoes": 163,
        }, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _erro_quota(exc):
        texto = str(exc).lower()
        return any(x in texto for x in ("429", "resource_exhausted", "quota exceeded", "rate limit"))

    @property
    def indice(self):
        if self._indice is not None:
            return self._indice
        try:
            from langchain_community.vectorstores import FAISS
        except ImportError as exc:
            raise RuntimeError("Instale langchain-community e faiss-cpu.") from exc
        docs = self._documentos_para_lc()
        total = len(docs)
        manifesto = self._ler_manifesto()
        atual = self._hash()
        mesma_versao = (
            manifesto.get("hash_documentos") == atual
            and manifesto.get("modelo_embedding") == self.config.modelo_embedding
            and manifesto.get("pipeline") == self.config.versao_pipeline_carta_completa
        )
        caminho = self.config.caminho_faiss_carta_completa
        indice = None
        inicio = 0
        if mesma_versao and manifesto.get("completo") is True and int(manifesto.get("documentos_embutidos", 0)) == total and caminho.exists():
            self._indice = FAISS.load_local(str(caminho), self.embeddings_service.embeddings, allow_dangerous_deserialization=True)
            return self._indice
        if mesma_versao and caminho.exists() and 0 < int(manifesto.get("documentos_embutidos", 0)) < total:
            inicio = int(manifesto["documentos_embutidos"])
            indice = FAISS.load_local(str(caminho), self.embeddings_service.embeddings, allow_dangerous_deserialization=True)
            print(f"🔄 Retomando FAISS da Carta completa: {inicio}/{total} documentos.")
        elif caminho.exists() and not mesma_versao:
            print("♻️ Corpus/modelo mudou: reconstruindo o índice granular da Carta.")
        for lote_inicio in range(inicio, total, self.config.lote_embedding_carta_completa):
            lote_fim = min(lote_inicio + self.config.lote_embedding_carta_completa, total)
            lote = docs[lote_inicio:lote_fim]
            for tentativa in range(1, self.config.max_tentativas_lote_embedding + 1):
                try:
                    if indice is None:
                        indice = FAISS.from_documents(lote, self.embeddings_service.embeddings)
                    else:
                        indice.add_documents(lote)
                    break
                except Exception as exc:
                    if not self._erro_quota(exc) or tentativa >= self.config.max_tentativas_lote_embedding:
                        raise
                    time.sleep(self.config.pausa_entre_lotes_embedding)
            caminho.parent.mkdir(parents=True, exist_ok=True)
            indice.save_local(str(caminho))
            completo = lote_fim == total
            self._salvar_manifesto(total, lote_fim, completo)
            if not completo:
                time.sleep(self.config.pausa_entre_lotes_embedding)
        self._indice = indice
        return self._indice
