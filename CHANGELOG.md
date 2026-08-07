# Changelog

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
