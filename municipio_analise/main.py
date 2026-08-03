# =====================================================
# EXECUÇÃO PRINCIPAL
# =====================================================
import json

import pandas as pd

from . import config
from .analise import gerar_analise_dimensao, gerar_analise_geral
from .classificacao import (
    CHUNKS_GERAIS,
    DIMENSOES,
    INDICADORES_NAO_CLASSIFICADOS,
    classificar_indicador,
)
from .dados_carta import CHUNKS_CARTA
from .prompts import criar_chains
from .rag import (
    carregar_ou_construir_indice_chunks,
    carregar_ou_construir_indice_topicos,
    criar_classificador_por_embedding,
    criar_embeddings,
    criar_llm,
)
from .relatorio import gerar_relatorio_word
from .utils import classificar_porte

DIMENSAO_PARA_CHAVE = {
    "Econômica": "economica",
    "Sociocultural": "sociocultural",
    "Meio Ambiente": "meio_ambiente",
    "Capacidades Institucionais": "capacidades_institucionais",
}


def main():
    config.validar_configuracao()

    # --- Modelos e índices semânticos ---
    embeddings = criar_embeddings()
    llm = criar_llm()
    chain_geral, chain_dimensao = criar_chains(llm)
    indice_chunks = carregar_ou_construir_indice_chunks(embeddings)
    indice_topicos = carregar_ou_construir_indice_topicos(embeddings)
    classificador_embedding = criar_classificador_por_embedding(indice_topicos)

    # --- Planilha ---
    try:
        df = pd.read_excel(config.ARQUIVO_PLANILHA)
    except FileNotFoundError:
        raise FileNotFoundError(f"Planilha de indicadores não encontrada: {config.ARQUIVO_PLANILHA}")

    df.columns = (
        df.columns.str.strip().str.lower().str.normalize("NFKD")
        .str.encode("ascii", errors="ignore").str.decode("utf-8")
    )

    municipios = df[config.COLUNA_MUNICIPIO].unique().tolist()
    print("\nMunicípios disponíveis:")
    for i, m in enumerate(municipios, 1):
        print(f"{i} - {m}")

    escolha = int(input("\nDigite o número do município: "))
    municipio = municipios[escolha - 1]

    dados = df[df[config.COLUNA_MUNICIPIO] == municipio].iloc[0]
    populacao = int(dados[config.COLUNA_POPULACAO])
    porte = classificar_porte(populacao)
    print(f"\n🔹 Porte identificado: {porte}")

    colunas_ignoradas = [config.COLUNA_MUNICIPIO, config.COLUNA_POPULACAO, "cod municipio", "estado", "avaliada"]
    candidatos_indicadores = dados.drop(
        labels=[c for c in colunas_ignoradas if c in dados.index]
    ).to_dict()

    # --- Classifica cada coluna candidata por dimensão/tópico ---
    # (colunas de metadado/agregado em COLUNAS_NAO_INDICADORES são
    # descartadas aqui mesmo, sem entrar em INDICADORES_NAO_CLASSIFICADOS)
    indicadores_por_dimensao = {d: {} for d in DIMENSOES}
    for nome, valor in candidatos_indicadores.items():
        classificacao = classificar_indicador(nome, classificador_embedding)
        if classificacao:
            indicadores_por_dimensao[classificacao["dimensao"]][nome] = valor

    # análise geral usa o conjunto de todos os indicadores já classificados
    # (não os brutos da planilha, para não incluir ruído/agregados)
    todos_indicadores = {
        nome: valor
        for indicadores in indicadores_por_dimensao.values()
        for nome, valor in indicadores.items()
    }

    for dimensao in DIMENSOES:
        if not indicadores_por_dimensao[dimensao]:
            print(f"⚠️  Dimensão '{dimensao}' ficou sem indicadores classificados.")

    if INDICADORES_NAO_CLASSIFICADOS:
        print(f"⚠️  Indicadores não classificados (revisar data/mapa_indicadores.json): "
              f"{sorted(set(INDICADORES_NAO_CLASSIFICADOS))}")

    # --- 5 chamadas ao modelo ---
    chunks_gerais = [CHUNKS_CARTA[f"geral_{t}"] for t in CHUNKS_GERAIS if f"geral_{t}" in CHUNKS_CARTA]

    print("🔹 Gerando análise geral...")
    analise_geral = gerar_analise_geral(chain_geral, municipio, porte, todos_indicadores, chunks_gerais)

    relatorio = {"analise_geral": analise_geral, "dimensoes": {}}
    for dimensao, chave in DIMENSAO_PARA_CHAVE.items():
        print(f"🔹 Gerando análise da dimensão {dimensao}...")
        relatorio["dimensoes"][chave] = gerar_analise_dimensao(
            chain_dimensao,
            dimensao=dimensao,
            municipio=municipio,
            porte=porte,
            indicadores_dimensao=indicadores_por_dimensao[dimensao],
            linha_planilha=dados,
            indice_chunks=indice_chunks,
            classificador_embedding=classificador_embedding,
        )

    print("\n" + json.dumps(relatorio, ensure_ascii=False, indent=2))

    gerar_relatorio_word(municipio, relatorio)
    print("✅ Processo finalizado com sucesso.")


if __name__ == "__main__":
    main()
