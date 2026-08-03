# =====================================================
# CHAMADAS AO MODELO (com validações e novas assinaturas)
# =====================================================
from .classificacao import selecionar_chunks_dimensao
from .prompts import INSTRUCAO_COM_BASE, INSTRUCAO_SEM_BASE


def _formatar_indicadores(indicadores: dict) -> str:
    return "\n".join(f"- {k}: {v}" for k, v in indicadores.items())


def _formatar_chunks(chunks: list) -> str:
    return "\n\n".join(f"[{c['topico']}] {c['texto']}" for c in chunks)


def gerar_analise_geral(chain_geral, municipio, porte, indicadores, chunks_gerais, tentativas=2):
    """Gera a análise institucional geral (2 parágrafos)."""
    if chunks_gerais:
        instrucao_base = INSTRUCAO_COM_BASE.format(base_conceitual=_formatar_chunks(chunks_gerais))
    else:
        instrucao_base = INSTRUCAO_SEM_BASE
    indicadores_txt = _formatar_indicadores(indicadores)

    ultimo_erro = None
    for _ in range(tentativas):
        try:
            resultado = chain_geral.invoke({
                "municipio": municipio, "porte": porte,
                "indicadores_txt": indicadores_txt, "instrucao_base": instrucao_base,
            })
            if not resultado.analise_geral or len(resultado.analise_geral.strip()) < 40:
                raise ValueError("Resposta do modelo vazia ou incompleta.")
            return resultado.analise_geral
        except Exception as e:  # resposta inválida do modelo
            ultimo_erro = e
            print(f"⚠️  Falha ao gerar análise geral, tentando novamente... ({e})")

    raise RuntimeError(f"Não foi possível gerar a análise geral após {tentativas} tentativas: {ultimo_erro}")


def gerar_analise_dimensao(chain_dimensao, dimensao, municipio, porte, indicadores_dimensao,
                            linha_planilha=None, tentativas=2, indice_chunks=None,
                            classificador_embedding=None):
    """Gera análise + exatamente 3 sugestões para uma dimensão."""
    if not indicadores_dimensao:
        raise ValueError(f"A dimensão '{dimensao}' não possui indicadores associados.")

    chunks_selecionados = selecionar_chunks_dimensao(
        dimensao, indicadores_dimensao, linha_planilha,
        indice_chunks=indice_chunks, classificador_embedding=classificador_embedding,
    )
    # separa os chunks gerais (sempre presentes) dos chunks setoriais, só
    # para decidir se existe base setorial específica para esta dimensão
    chunks_setoriais = [c for c in chunks_selecionados if c["dimensao"] != "Geral"]
    if chunks_selecionados:
        instrucao_base = INSTRUCAO_COM_BASE.format(base_conceitual=_formatar_chunks(chunks_selecionados))
    else:
        instrucao_base = INSTRUCAO_SEM_BASE
    if not chunks_setoriais:
        print(f"⚠️  Dimensão '{dimensao}': nenhum chunk setorial específico na Carta "
              f"(usando apenas chunks gerais e os indicadores como base).")

    indicadores_txt = _formatar_indicadores(indicadores_dimensao)

    ultimo_erro = None
    for _ in range(tentativas):
        try:
            resultado = chain_dimensao.invoke({
                "municipio": municipio, "porte": porte, "dimensao": dimensao,
                "indicadores_txt": indicadores_txt, "instrucao_base": instrucao_base,
            })
            if len(resultado.sugestoes) != 3:
                raise ValueError(f"Modelo retornou {len(resultado.sugestoes)} sugestões (esperado: 3).")
            if not resultado.analise or len(resultado.analise.strip()) < 30:
                raise ValueError("Análise da dimensão vazia ou incompleta.")
            return {"analise": resultado.analise, "sugestoes": resultado.sugestoes}
        except Exception as e:
            ultimo_erro = e
            print(f"⚠️  Falha ao gerar análise de '{dimensao}', tentando novamente... ({e})")

    raise RuntimeError(f"Não foi possível gerar a análise de '{dimensao}' após {tentativas} tentativas: {ultimo_erro}")
