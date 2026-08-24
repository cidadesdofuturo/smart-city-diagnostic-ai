# Changelog

## 0.3.0 — 2026-08-24

- sincronização do pacote `municipio_analise/` com o notebook-fonte de 18/08/2026;
- substituição do Gemini como LLM principal por Claude Sonnet 4.6 (`claude-sonnet-4-6`);
- Gemini mantido somente para `models/gemini-embedding-001` e FAISS;
- Claude Web Search movido para depois da geração do rascunho de cada dimensão;
- validação pós-rascunho de até cinco pontos prioritários, com enriquecimento nominal complementar;
- nova etapa explícita de revisão da dimensão após a validação web;
- RAG granular da Carta Brasileira para Cidades Inteligentes — Edição Revisada com 185 documentos;
- até cinco prioridades por dimensão, oito candidatos por prioridade e oito chunks finais;
- reranking por similaridade semântica, maturidade 0–7, dimensão, tópico e cobertura múltipla;
- suporte a dois ou três parágrafos por dimensão, mantendo exatamente quatro sugestões;
- Análise Geral movida para o final do pipeline, usando apenas as quatro dimensões finalizadas e sem nova pesquisa web;
- novo snapshot versionado do corpus granular e persistência/reconstrução local dos índices FAISS;
- configuração separada para `ANTHROPIC_API_KEY` e `GEMINI_API_KEY`;
- testes atualizados para a nova ordem do pipeline e nova configuração.

## 0.2.0 — 2026-08-07

- atualização integral a partir do notebook com validação web por dimensões;
- Google Search Grounding para contexto geral do município;
- uma pesquisa web de validação para cada uma das quatro dimensões;
- validação territorial por município, UF e código IBGE quando disponível;
- diferenciação entre ações planejadas, contratadas, em implantação e concluídas;
- análise dimensional alterada para exatamente dois parágrafos;
- sugestões dimensionais alteradas de três para exatamente quatro;
- relatório Word atualizado para preservar a separação entre parágrafos;
- testes do pipeline atualizados para cobrir pesquisa web e quatro sugestões;
- notebook-fonte corrente incluído no repositório.

## 0.1.0 — 2026-08-07

- reconstrução integral a partir do notebook corrente;
- `gemini-3.6-flash` como LLM;
- maturidade de indicadores em escala 0–7;
- remoção de `temperature`, `top_p` e `top_k` do cliente Gemini 3.6;
- separação de mapas/chunks em JSON;
- pipeline único `Config + PipelineAnaliseMunicipio`;
- tratamento de valores ausentes para não enviar `NaN` ao LLM;
- testes unitários e GitHub Actions;
- notebook Colab reduzido a uma interface do pacote.
