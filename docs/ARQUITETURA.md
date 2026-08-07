# Arquitetura

O fluxo canônico é `Config -> PipelineAnaliseMunicipio`.

1. A planilha é carregada e as colunas são normalizadas.
2. Indicadores são classificados por mapa explícito, palavras-chave e fallback semântico.
3. O nível de maturidade 0–7 vem prioritariamente das colunas `N M Indicador...`.
4. A maturidade ordena os tópicos da Carta usados no contexto RAG.
5. Dados contextuais complementam a análise, sem calcular maturidade.
6. O Gemini com Google Search Grounding realiza uma pesquisa breve do município.
7. O Gemini gera a análise geral estruturada em dois parágrafos.
8. Para cada dimensão, é feita uma pesquisa web de validação/atualização.
9. Cada análise dimensional retorna exatamente dois parágrafos e quatro sugestões.
10. O resultado é salvo em `.docx`, preservando os parágrafos separadamente.

## Papel da pesquisa web

A web é uma camada complementar. Ela não altera os níveis da planilha e não substitui a base de indicadores. Serve para identificar fatos recentes que possam qualificar a leitura, como obras, programas, contratos, ampliações e implantações em andamento.

## Índices FAISS

- `faiss_index_topicos`: fallback semântico para classificar indicadores novos.
- `faiss_index_chunks`: busca semântica de trechos da Carta quando um tópico não tem chunk direto.

Os índices são persistidos na pasta de dados e não devem ser versionados no Git.
