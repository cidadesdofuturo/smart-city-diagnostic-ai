# Metodologia implementada

Esta implementação reproduz a lógica do notebook corrente fornecido em agosto de 2026, incluindo pesquisa web geral e validação web por dimensão.

- Dimensões: Econômica, Sociocultural, Meio Ambiente e Capacidades Institucionais.
- Escala de maturidade dos indicadores: 0 a 7.
- 88 relações indicador -> coluna de maturidade.
- 85 indicadores possuem mapeamento setorial explícito na taxonomia atual.
- 20 chunks temáticos pré-extraídos da Carta Brasileira para Cidades Inteligentes.
- 23 campos socioeconômicos/institucionais são tratados como dados contextuais.
- Análise geral: dois parágrafos.
- Análise por dimensão: exatamente dois parágrafos e quatro sugestões.

## Dados contextuais

Dados contextuais podem caracterizar o município e a dimensão correspondente. Eles não são indicadores de maturidade e não entram na priorização dos tópicos.

## Pesquisa web geral

A pesquisa geral busca apenas fatos úteis e relativamente estáveis para contextualizar o município. A identidade territorial é conferida por município, UF e, quando disponível, código IBGE.

## Validação web por dimensão

Cada dimensão recebe uma pesquisa curta, orientada pelos próprios indicadores. Ela procura fatos recentes que possam qualificar a interpretação, especialmente obras, programas, sistemas, contratos, licitações, expansões e alterações institucionais formalizadas.

A pesquisa web:

- não recalcula maturidade;
- não substitui os indicadores da planilha;
- diferencia planejamento, contratação, implantação e operação;
- não considera uma obra em andamento como resultado já alcançado;
- não força resultados quando não há informação confiável;
- ajuda a evitar recomendações já superadas por ações comprovadamente em execução.

## Limitação mantida da fonte

Três indicadores de Habitação possuem coluna de maturidade, mas não têm mapeamento explícito na taxonomia setorial do notebook-fonte. Eles podem chegar ao fallback por palavras-chave/embeddings, porém não foram artificialmente remapeados nesta reconstrução.
