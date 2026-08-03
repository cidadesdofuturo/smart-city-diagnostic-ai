# =====================================================
# ESTRUTURA DE DIMENSÕES E TÓPICOS
# =====================================================
"""Taxonomia de dimensões/tópicos e classificação de indicadores.

O mapa indicador -> {dimensao, topico, chunk_id} e as colunas de metadado
da planilha (data/mapa_indicadores.json, data/mapa_nivel_maturidade.json e
data/colunas_nao_indicadores.json) foram construídos a partir da estrutura
real da planilha `indicadores.xlsx`: 85 indicadores setoriais nas 4
dimensões, cada um seguido, na própria planilha, por uma coluna
"N M Indicador..." com o nível de maturidade (0-5) já calculado para
aquele indicador.

3 indicadores do grupo "Habitação" (dimensão Econômica) não têm tópico
correspondente na taxonomia dos 30 tópicos e por isso NÃO entram no mapa
(ficam registrados em INDICADORES_NAO_CLASSIFICADOS quando encontrados na
planilha): "Percentual de domicílios com população vivendo em
aglomerados subnormais", "Assentamentos urbanos precários" e "Programas e
ações habitacionais".
"""

import json
from pathlib import Path

from .dados_carta import CHUNKS_CARTA, TOPICOS_SEM_CHUNK_NA_CARTA
from .utils import normalizar

_DATA_DIR = Path(__file__).parent / "data"


def _carregar_json(nome_arquivo):
    with open(_DATA_DIR / nome_arquivo, encoding="utf-8") as f:
        return json.load(f)


CHUNKS_GERAIS = [
    "conceito_brasileiro_de_cidades_inteligentes",
    "diversidade_territorial_e_reducao_de_desigualdades",
    "transformacao_digital_adaptada_a_capacidade_municipal",
]
CHUNKS_ECONOMICA = [
    "agua_e_esgoto", "residuos_solidos", "transporte", "vias_publicas",
    "conectividade", "inovacao", "gestao_urbana", "servicos_online", "dados_abertos",
]
CHUNKS_SOCIOCULTURAL = [
    "educacao", "cultura_e_esporte", "saude", "seguranca_publica",
    "defesa_civil", "inclusao_digital", "inclusao_e_equidade", "participacao_cidada",
]
CHUNKS_MEIO_AMBIENTE = [
    "agua_e_saneamento", "residuos_solidos", "areas_verdes",
    "qualidade_do_ar_e_emissoes", "energia_e_iluminacao_publica",
]
CHUNKS_CAPACIDADES_INSTITUCIONAIS = [
    "governanca_e_planejamento", "infraestrutura_de_ti", "servicos_publicos_digitais",
    "monitoramento_e_transparencia", "dados_e_seguranca_da_informacao",
]

# dimensão -> (prefixo do chunk_id, lista de tópicos)
DIMENSOES = {
    "Econômica": {"prefixo": "economica", "topicos": CHUNKS_ECONOMICA},
    "Sociocultural": {"prefixo": "sociocultural", "topicos": CHUNKS_SOCIOCULTURAL},
    "Meio Ambiente": {"prefixo": "meio_ambiente", "topicos": CHUNKS_MEIO_AMBIENTE},
    "Capacidades Institucionais": {"prefixo": "institucional", "topicos": CHUNKS_CAPACIDADES_INSTITUCIONAIS},
}

# Palavras-chave por tópico — usadas apenas para classificar indicadores
# (não são trechos da Carta, são termos de busca).
PALAVRAS_CHAVE_TOPICO = {
    "agua_e_esgoto": ["água", "esgoto", "saneamento básico", "abastecimento"],
    "residuos_solidos": ["resíduos sólidos", "lixo", "coleta seletiva", "reciclagem"],
    "transporte": ["transporte público", "mobilidade urbana", "ônibus"],
    "vias_publicas": ["vias públicas", "pavimentação", "trânsito", "mobiliário urbano"],
    "conectividade": ["conectividade", "internet", "banda larga", "wi-fi"],
    "inovacao": ["inovação", "empreendedorismo", "startups"],
    "gestao_urbana": ["gestão urbana", "planejamento urbano", "uso do solo", "plano diretor"],
    "servicos_online": ["serviços online", "serviços digitais", "atendimento digital", "governo digital"],
    "dados_abertos": ["dados abertos", "portal de dados", "transparência de dados"],
    "educacao": ["educação", "escola", "ensino"],
    "cultura_e_esporte": ["cultura", "esporte", "lazer"],
    "saude": ["saúde", "atenção primária", "telessaúde", "telemedicina"],
    "seguranca_publica": ["segurança pública", "violência", "policiamento"],
    "defesa_civil": ["defesa civil", "risco", "desastre"],
    "inclusao_digital": ["inclusão digital", "acesso digital", "letramento digital"],
    "inclusao_e_equidade": ["inclusão", "equidade", "acessibilidade", "grupos vulneráveis"],
    "participacao_cidada": ["participação cidadã", "participação social", "controle social"],
    "agua_e_saneamento": ["água", "saneamento", "recursos hídricos"],
    "areas_verdes": ["áreas verdes", "parques", "arborização"],
    "qualidade_do_ar_e_emissoes": ["qualidade do ar", "emissões", "poluição"],
    "energia_e_iluminacao_publica": ["energia", "iluminação pública", "eficiência energética"],
    "governanca_e_planejamento": ["governança", "planejamento estratégico", "plano diretor"],
    "infraestrutura_de_ti": ["infraestrutura de ti", "tecnologia da informação", "sistemas municipais"],
    "servicos_publicos_digitais": ["serviços públicos digitais", "digitalização"],
    "monitoramento_e_transparencia": ["monitoramento", "transparência", "prestação de contas"],
    "dados_e_seguranca_da_informacao": ["proteção de dados", "segurança da informação", "lgpd"],
}


# =====================================================
# MAPA ENTRE INDICADORES, DIMENSÕES E TÓPICOS
# =====================================================
_MAPA_INDICADORES_BRUTO = _carregar_json("mapa_indicadores.json")
_MAPA_NIVEL_MATURIDADE_BRUTO = _carregar_json("mapa_nivel_maturidade.json")

MAPA_INDICADORES = {normalizar(k): v for k, v in _MAPA_INDICADORES_BRUTO.items()}
MAPA_NIVEL_MATURIDADE = {normalizar(k): normalizar(v) for k, v in _MAPA_NIVEL_MATURIDADE_BRUTO.items()}

# Colunas que NÃO são indicadores individuais: dados cadastrais/socioeconômicos
# de contexto (PIB, IDH, GINI etc.), colunas "N M Indicador..." (nível de
# maturidade de cada indicador — já usadas via MAPA_NIVEL_MATURIDADE) e
# colunas de agregado por tópico/dimensão (ex.: "Água e esgoto" como score
# somado do tópico, "Econômica" como score da dimensão). Sem essa lista,
# o classificador por palavra-chave acabaria tratando esses agregados como
# se fossem indicadores individuais (ex.: a coluna-agregado "Saúde" seria
# capturada pela mesma palavra-chave do tópico "saude").
COLUNAS_NAO_INDICADORES = {normalizar(c) for c in _carregar_json("colunas_nao_indicadores.json")}

INDICADORES_NAO_CLASSIFICADOS = []  # preenchida em tempo de execução


def classificar_indicador(nome_indicador, classificador_embedding=None):
    """Retorna {dimensao, topico, chunk_id} para um indicador, ou None.

    Ordem de resolução:
    1) correspondência exata em MAPA_INDICADORES;
    2) fallback por palavra-chave (nome do indicador x PALAVRAS_CHAVE_TOPICO)
       — útil para indicadores novos, ainda não presentes no mapa;
    3) fallback por similaridade semântica de embeddings (nome do indicador
       x tópicos, via classificador_embedding, se fornecido) — útil quando
       o indicador usa vocabulário diferente do das palavras-chave cadastradas;
    4) se nada for encontrado, registra em INDICADORES_NAO_CLASSIFICADOS.
    """
    if nome_indicador in COLUNAS_NAO_INDICADORES:
        return None  # metadado/agregado conhecido — não é um indicador setorial

    if nome_indicador in MAPA_INDICADORES:
        return MAPA_INDICADORES[nome_indicador]

    nome_norm = normalizar(nome_indicador)
    melhor, melhor_score = None, 0
    for dimensao, info in DIMENSOES.items():
        for topico in info["topicos"]:
            palavras = PALAVRAS_CHAVE_TOPICO.get(topico, [])
            score = sum(1 for p in palavras if normalizar(p) in nome_norm)
            if score > melhor_score:
                melhor_score = score
                melhor = {"dimensao": dimensao, "topico": topico.replace("_", " ").title(),
                          "chunk_id": f"{info['prefixo']}_{topico}"}

    if melhor:
        return melhor

    if classificador_embedding is not None:
        classificacao_embedding = classificador_embedding(nome_indicador)
        if classificacao_embedding:
            return classificacao_embedding

    INDICADORES_NAO_CLASSIFICADOS.append(nome_indicador)
    return None


# =====================================================
# NÍVEL DE MATURIDADE E SELEÇÃO DE CHUNKS POR DIMENSÃO
# =====================================================
import pandas as pd

NIVEIS_TEXTUAIS = {
    "inexistente": 0, "nao": 0, "não": 0, "ausente": 0,
    "inicial": 1, "basico": 1, "básico": 1,
    "em desenvolvimento": 2, "em implantacao": 2, "em implantação": 2,
    "intermediario": 3, "intermediário": 3,
    "avancado": 4, "avançado": 4,
    "consolidado": 5, "sim": 5,
}


def estimar_nivel_indicador(valor):
    """Estima um nível de maturidade (0 a 5) a partir do valor bruto do
    indicador (fallback, usado quando não há coluna N M Indicador
    pareada). Retorna None quando não é possível estimar — nesse caso o
    indicador não entra na priorização, mas continua disponível ao modelo."""
    if pd.isna(valor):
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    return NIVEIS_TEXTUAIS.get(normalizar(valor))


def obter_nivel_indicador(nome_indicador, valor, linha_planilha=None):
    """Retorna o nível de maturidade (0-5) de um indicador, priorizando a
    coluna oficial "N M Indicador..." da planilha (via
    MAPA_NIVEL_MATURIDADE) e caindo para a estimativa por texto quando
    essa coluna não existir ou não puder ser lida."""
    nm_col = MAPA_NIVEL_MATURIDADE.get(nome_indicador)
    if nm_col is not None and linha_planilha is not None and nm_col in linha_planilha.index:
        nivel_real = linha_planilha[nm_col]
        if not pd.isna(nivel_real):
            try:
                return float(nivel_real)
            except (TypeError, ValueError):
                pass
    return estimar_nivel_indicador(valor)


def selecionar_chunks_dimensao(dimensao, indicadores_dimensao, linha_planilha=None,
                                usar_fallback_semantico=True, indice_chunks=None,
                                classificador_embedding=None):
    """Seleciona os chunks relevantes para uma dimensão:
    - todos os chunks gerais;
    - chunks dos tópicos que têm ao menos um indicador classificado nesta
      dimensão, ordenados dos indicadores de menor maturidade para os de
      maior (prioriza o que precisa de mais atenção);
    - nunca inclui chunks de outra dimensão;
    - tópicos sem chunk direto na Carta (ver TOPICOS_SEM_CHUNK_NA_CARTA):
      se usar_fallback_semantico=True e um indice_chunks (FAISS) for
      fornecido, busca por similaridade de embeddings o chunk mais próximo
      dentro da MESMA dimensão; se não encontrar nada (ou o fallback
      estiver desligado), o tópico simplesmente fica sem chunk (nunca
      inventa conteúdo).
    """
    chunks_gerais = [CHUNKS_CARTA[f"geral_{t}"] for t in CHUNKS_GERAIS if f"geral_{t}" in CHUNKS_CARTA]

    pior_nivel_por_chunk = {}
    for nome, valor in indicadores_dimensao.items():
        classificacao = classificar_indicador(nome, classificador_embedding)
        if not classificacao or classificacao["dimensao"] != dimensao:
            continue
        nivel = obter_nivel_indicador(nome, valor, linha_planilha)
        chunk_id = classificacao["chunk_id"]
        nivel_efetivo = 99 if nivel is None else nivel
        pior_nivel_por_chunk[chunk_id] = min(pior_nivel_por_chunk.get(chunk_id, 99), nivel_efetivo)

    topicos_ordenados = sorted(pior_nivel_por_chunk, key=lambda cid: pior_nivel_por_chunk[cid])

    chunks_topicos = []
    chunk_ids_incluidos = set()
    for cid in topicos_ordenados:
        if cid in CHUNKS_CARTA:
            chunks_topicos.append(CHUNKS_CARTA[cid])
            chunk_ids_incluidos.add(cid)
        elif usar_fallback_semantico and cid in TOPICOS_SEM_CHUNK_NA_CARTA and indice_chunks is not None:
            nome_topico = cid.split("_", 1)[1].replace("_", " ")
            resultados = indice_chunks.similarity_search(
                nome_topico, k=1, filter={"dimensao": dimensao}, fetch_k=50
            )
            for doc in resultados:
                chunk_id_encontrado = doc.metadata["chunk_id"]
                if chunk_id_encontrado not in chunk_ids_incluidos:
                    chunks_topicos.append(CHUNKS_CARTA[chunk_id_encontrado])
                    chunk_ids_incluidos.add(chunk_id_encontrado)

    return chunks_gerais + chunks_topicos
