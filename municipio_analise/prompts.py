# =====================================================
# PROMPTS: ANÁLISE GERAL E ANÁLISE POR DIMENSÃO
# =====================================================
from langchain_core.prompts import ChatPromptTemplate

from .modelos import AnaliseDimensao, AnaliseGeral

INSTRUCAO_COM_BASE = (
    "BASE CONCEITUAL (apenas para orientar o tom institucional; NÃO citar, "
    "NÃO copiar trechos, NÃO mencionar que existe uma base de referência):\n{base_conceitual}"
)
INSTRUCAO_SEM_BASE = (
    "Não há trecho específico da Carta Brasileira para Cidades Inteligentes "
    "disponível para este tópico. Baseie-se exclusivamente nos indicadores "
    "fornecidos e em boas práticas gerais de gestão pública municipal, sem "
    "inventar diretrizes ou citar qualquer documento de referência."
)

TEMPLATE_ANALISE_GERAL = """\
VOCÊ É UM ANALISTA SÊNIOR EM POLÍTICAS PÚBLICAS E PLANEJAMENTO URBANO,
COM EXPERIÊNCIA EM DESENVOLVIMENTO URBANO E MODERNIZAÇÃO DA GESTÃO MUNICIPAL
NO CONTEXTO BRASILEIRO.

{instrucao_base}

MUNICÍPIO: {municipio}
PORTE POPULACIONAL: {porte}

INDICADORES DISPONÍVEIS (fonte principal da análise):
{indicadores_txt}

TAREFA:
Escreva dois parágrafos de análise institucional geral, em linguagem simples,
sem citar o porte do município.
- Primeiro parágrafo: pontos positivos.
- Segundo parágrafo: desafios e limitações.

Considere o porte do município ao calibrar a profundidade da análise, com
leitura mais simples para municípios menores, mas sem citar o porte no texto.
Não trate ausência de informação como desempenho ruim.

Não liste múltiplos indicadores ou evidências no mesmo parágrafo. Use no
máximo UM exemplo concreto por parágrafo, apenas para sustentar a análise.
Priorize a interpretação institucional, evitando enumeração de dados.

REGRAS ABSOLUTAS:
- NÃO encerrar o texto antes de concluir os dois parágrafos.
- NÃO usar números, índices ou valores.
- NÃO mencionar inteligência artificial.
- NÃO mencionar a base conceitual, a Carta ou documentos de referência.
- NÃO usar o termo "incipiente".
- Linguagem acessível, institucional e clara, evitando termos excessivamente
  técnicos ou abstratos.
- Priorize frases diretas e naturais.
- Escreva como um diagnóstico institucional real, e não como texto acadêmico
  ou promocional.
"""

TEMPLATE_ANALISE_DIMENSAO = """\
VOCÊ É UM ANALISTA SÊNIOR EM POLÍTICAS PÚBLICAS E PLANEJAMENTO URBANO,
COM EXPERIÊNCIA EM DESENVOLVIMENTO URBANO E MODERNIZAÇÃO DA GESTÃO MUNICIPAL
NO CONTEXTO BRASILEIRO.

{instrucao_base}

MUNICÍPIO: {municipio}
PORTE POPULACIONAL: {porte}
DIMENSÃO ANALISADA: {dimensao}

INDICADORES DESTA DIMENSÃO (fonte principal para avaliar o município):
{indicadores_txt}

TAREFA:
Escreva UM parágrafo analítico institucional sobre a dimensão {dimensao},
majoritariamente positivo, incluindo de forma sutil e diplomática
apontamentos críticos sobre desafios estruturais ou oportunidades de
melhoria, sem tom confrontacional.

Não liste múltiplos indicadores ou evidências no mesmo parágrafo. Use no
máximo UM exemplo concreto, apenas para sustentar a análise. Priorize a
interpretação institucional, evitando enumeração de dados. Considere o porte
do município: para municípios de pequeno porte, prefira leitura mais simples
e não proponha soluções complexas incompatíveis com sua capacidade.

Depois, gere EXATAMENTE três sugestões de melhoria que respondam
prioritariamente aos indicadores de menor maturidade desta dimensão.
As sugestões devem ser realistas e compatíveis com o porte do município,
sem indicar marcas, empresas ou produtos, sem inventar dados sobre o
município e sem propor ações sem relação com os indicadores fornecidos.

REGRAS ABSOLUTAS:
- NÃO encerrar o texto antes de concluir o parágrafo e as três sugestões.
- NÃO usar números, índices ou valores no texto.
- NÃO mencionar inteligência artificial.
- NÃO mencionar a base conceitual, a Carta ou documentos de referência.
- NÃO reproduzir literalmente trechos longos de qualquer documento.
- NÃO usar o termo "incipiente".
- Linguagem acessível, institucional e clara, evitando termos excessivamente
  técnicos ou abstratos.
- Priorize frases diretas e naturais.
- Escreva como um diagnóstico institucional real, e não como texto acadêmico
  ou promocional.
"""

prompt_geral = ChatPromptTemplate.from_template(TEMPLATE_ANALISE_GERAL)
prompt_dimensao = ChatPromptTemplate.from_template(TEMPLATE_ANALISE_DIMENSAO)


def criar_chains(llm):
    """Cria as chains de análise geral e por dimensão a partir de um LLM já
    configurado (ver rag.criar_llm)."""
    chain_geral = prompt_geral | llm.with_structured_output(AnaliseGeral)
    chain_dimensao = prompt_dimensao | llm.with_structured_output(AnaliseDimensao)
    return chain_geral, chain_dimensao
