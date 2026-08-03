# =====================================================
# CHUNKS TEMÁTICOS DA CARTA (pré-extraídos do PDF oficial)
# =====================================================
"""Carrega os chunks temáticos da "Carta Brasileira para Cidades
Inteligentes" (versão oficial em PDF, 180 páginas, seção "2.5 Objetivos
estratégicos e recomendações").

Processo de extração (feito uma única vez, fora deste projeto):
1. Texto extraído com pdftotext -layout, isolando a coluna de corpo de
   texto e descartando a legenda lateral de atores (GF, GE, GM, ...).
2. As 122 recomendações numeradas (ex.: "2.8.1 Sustentabilidade em
   iluminação pública") foram identificadas e mantidas com redação
   original, sem cortes no meio de uma recomendação.
3. Cada recomendação foi classificada, por palavras-chave de título e
   corpo, no tópico de maior aderência dentro da estrutura de dimensões
   (ver classificacao.py). Recomendações sobre o mesmo tema foram
   reunidas em um único chunk (sem depender da posição no documento),
   respeitando ~250-500 tokens por chunk e sem sobreposição (overlap)
   entre chunks.

IMPORTANTE: nem todos os tópicos planejados têm conteúdo dedicado na Carta
(ela é organizada por 8 objetivos transversais de transformação digital,
não por setores como saúde, transporte ou saneamento). Os tópicos listados
em TOPICOS_SEM_CHUNK_NA_CARTA ficam sem chunk correspondente e são tratados
via fallback semântico (ver classificacao.selecionar_chunks_dimensao).
"""

import json
from pathlib import Path

_DATA_DIR = Path(__file__).parent / "data"


def _carregar_json(nome_arquivo):
    with open(_DATA_DIR / nome_arquivo, encoding="utf-8") as f:
        return json.load(f)


CHUNKS_CARTA = _carregar_json("carta_chunks.json")  # chunk_id -> {chunk_id, dimensao, topico, texto, fonte}
TOPICOS_SEM_CHUNK_NA_CARTA = _carregar_json("topicos_sem_chunk_na_carta.json")
