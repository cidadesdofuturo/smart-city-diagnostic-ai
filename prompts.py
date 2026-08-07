"""Templates de prompt sincronizados com o notebook de referência."""
from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from .modelos import AnaliseGeral, AnaliseDimensao

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

DADOS CONTEXTUAIS DO MUNICÍPIO
{dados_contextuais_txt}

INDICADORES DISPONÍVEIS
{indicadores_txt}


ESTRUTURA OBRIGATÓRIA — SIGA RIGOROSAMENTE:


Considerar o porte do município em todos os textos, com análises mais simples
para municípios menores. Não sugerir soluções complexas incompatíveis com
municípios de pequeno porte. Não usar o termo incipiente.
- Não listar múltiplos indicadores ou evidências no mesmo parágrafo
- No máximo UM exemplo concreto por parágrafo, usado apenas para sustentar a análise
- Priorizar interpretação institucional, evitando enumeração de dados


→ Dois parágrafos de análise institucional geral, linguagem simples, não citar o porte do município
   - Primeiro parágrafo: pontos positivos
   - Segundo parágrafo: desafios e limitações

REGRAS ABSOLUTAS:
- NÃO encerrar o texto antes de concluir TODAS as partes
- NÃO usar números, índices ou valores
- NÃO mencionar inteligência artificial
- NÃO mencionar a base conceitual ou documentos de referência
- Linguagem acessível, institucional e clara
- Evitar linguagem excessivamente técnica ou abstrata
- Priorizar frases mais diretas e naturais
- Escrever como um diagnóstico institucional real,
  e não como texto acadêmico ou promocional
  Regras obrigatórias:

Utilize linguagem técnica, mas simples e direta.
Priorize frases de tamanho curto ou médio.
Descreva os resultados encontrados antes de fazer interpretações.
Evite elogios excessivos ao município.
Evite transformar todo resultado positivo em uma "potencialidade" ou todo resultado negativo em uma "oportunidade".
Não utilize linguagem de consultoria, marketing ou textos promocionais.
Evite conclusões genéricas que não estejam diretamente relacionadas aos indicadores analisados.
Não exagere a importância dos resultados.
Quando houver aspectos positivos e negativos, apresente-os de maneira equilibrada e factual.
As recomendações devem ser práticas e compatíveis com os problemas identificados.

EVITE EXPRESSÕES TÍPICAS DE TEXTOS GERADOS POR IA, como:

"pilares robustos"
"ambiente fértil"
"potencial significativo"
"caminho promissor"
"desafios significativos"
"oportunidades estratégicas"
"ativo valioso"
"efervescência"
"impulsionar a inovação"
"elevar a eficiência"
"fortalecer a visão de futuro"
"representa uma oportunidade"
"demonstra sólido compromisso"
"se destaca por"
"é fundamental para"
"desempenha papel fundamental"

Também evite iniciar repetidamente os parágrafos com construções como:

"O município demonstra..."
"O município apresenta..."
"Viçosa demonstra..."
"Destaca-se..."
"Observa-se que..."
"Percebe-se que..."

Varie a construção das frases de forma natural.

PREFIRA formulações mais concretas.

Em vez de:
"O município demonstra um sólido compromisso com a transformação digital."

Escreva:
"O município já oferece parte dos serviços públicos pela internet e utiliza sistemas digitais em algumas áreas da administração."

Em vez de:
"Esse cenário representa uma oportunidade estratégica para ampliar a inovação."

Escreva:
"Esses serviços ainda podem ser ampliados e integrados."

Em vez de:
"A presença das universidades cria um ambiente fértil para a inovação."

Escreva:
"A presença das universidades facilita a aproximação entre a prefeitura, pesquisadores e empresas locais."

Não invente benefícios, causas ou relações que não estejam sustentadas pelos indicadores fornecidos.
"""

TEMPLATE_ANALISE_DIMENSAO = """\
VOCÊ É UM ANALISTA SÊNIOR EM POLÍTICAS PÚBLICAS, TRANSFORMAÇÃO DIGITAL
E PLANEJAMENTO URBANO MUNICIPAL NO CONTEXTO BRASILEIRO.

{instrucao_base}

MUNICÍPIO: {municipio}
PORTE POPULACIONAL: {porte}
DIMENSÃO ANALISADA: {dimensao}

INDICADORES DA DIMENSÃO:
{indicadores_txt}

DADOS CONTEXTUAIS DA DIMENSÃO
{dados_contextuais_txt}

TAREFA:
Produza um parágrafo institucional equilibrado sobre a dimensão
{dimensao}, seguido de exatamente três sugestões de melhoria.

ANÁLISE DA DIMENSÃO:
- Apresente primeiro os resultados favoráveis efetivamente sustentados pelos
  indicadores.
- Em seguida, apresente os principais desafios e oportunidades de melhoria.
- Quando houver resultados contrastantes, explique claramente a diferença.



REGRAS ABSOLUTAS:
- NÃO encerrar o texto antes de concluir TODAS as partes
- NÃO usar números, índices ou valores
- NÃO mencionar inteligência artificial
- NÃO mencionar a base conceitual ou documentos de referência
- Linguagem acessível, institucional e clara
- Evitar linguagem excessivamente técnica ou abstrata
- Priorizar frases mais diretas e naturais
- Escrever como um diagnóstico institucional real,
  e não como texto acadêmico ou promocional
  Regras obrigatórias:

Utilize linguagem técnica, mas simples e direta.
Priorize frases de tamanho curto ou médio.
Descreva os resultados encontrados antes de fazer interpretações.
Evite elogios excessivos ao município.
Evite transformar todo resultado positivo em uma "potencialidade" ou todo resultado negativo em uma "oportunidade".
Não utilize linguagem de consultoria, marketing ou textos promocionais.
Evite conclusões genéricas que não estejam diretamente relacionadas aos indicadores analisados.
Não exagere a importância dos resultados.
Quando houver aspectos positivos e negativos, apresente-os de maneira equilibrada e factual.
As recomendações devem ser práticas e compatíveis com os problemas identificados.

EVITE EXPRESSÕES TÍPICAS DE TEXTOS GERADOS POR IA, como:

"pilares robustos"
"ambiente fértil"
"potencial significativo"
"caminho promissor"
"desafios significativos"
"oportunidades estratégicas"
"ativo valioso"
"efervescência"
"impulsionar a inovação"
"elevar a eficiência"
"fortalecer a visão de futuro"
"representa uma oportunidade"
"demonstra sólido compromisso"
"se destaca por"
"é fundamental para"
"desempenha papel fundamental"

Também evite iniciar repetidamente os parágrafos com construções como:

"O município demonstra..."
"O município apresenta..."
"Viçosa demonstra..."
"Destaca-se..."
"Observa-se que..."
"Percebe-se que..."

Varie a construção das frases de forma natural.

PREFIRA formulações mais concretas.

Em vez de:
"O município demonstra um sólido compromisso com a transformação digital."

Escreva:
"O município já oferece parte dos serviços públicos pela internet e utiliza sistemas digitais em algumas áreas da administração."

Em vez de:
"Esse cenário representa uma oportunidade estratégica para ampliar a inovação."

Escreva:
"Esses serviços ainda podem ser ampliados e integrados."

Em vez de:
"A presença das universidades cria um ambiente fértil para a inovação."

Escreva:
"A presença das universidades facilita a aproximação entre a prefeitura, pesquisadores e empresas locais."

Não invente benefícios, causas ou relações que não estejam sustentadas pelos indicadores fornecidos.
"""

prompt_geral = ChatPromptTemplate.from_template(TEMPLATE_ANALISE_GERAL)
prompt_dimensao = ChatPromptTemplate.from_template(TEMPLATE_ANALISE_DIMENSAO)



def criar_chains(llm):
    """Cria as duas chains com saída estruturada, como no notebook."""
    llm_estruturado_geral = llm.with_structured_output(AnaliseGeral)
    llm_estruturado_dimensao = llm.with_structured_output(AnaliseDimensao)
    chain_geral = prompt_geral | llm_estruturado_geral
    chain_dimensao = prompt_dimensao | llm_estruturado_dimensao
    return chain_geral, chain_dimensao
