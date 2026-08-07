# Smart City Diagnostic AI

[Versão em português](README.md)

Municipal diagnostic pipeline for the **Cidades do Futuro Program**, combining municipal indicators, the Brazilian Smart Cities Charter, semantic retrieval, structured Gemini outputs, and controlled web validation.

The canonical API is `Config + PipelineAnaliseMunicipio`. The current source notebook is preserved at [`notebooks/notebook_fonte_validacao_web.ipynb`](notebooks/notebook_fonte_validacao_web.ipynb).

## Main features

- reads `indicadores.xlsx`;
- classifies indicators into four dimensions and thematic topics;
- uses a **0–7 maturity scale**;
- uses embeddings and FAISS for semantic fallback and retrieval;
- treats contextual fields as context, not maturity indicators;
- performs a brief municipality-level Google Search Grounding step;
- performs one targeted web-validation step per dimension;
- keeps spreadsheet indicators as the primary diagnostic source;
- produces a two-paragraph overall analysis;
- produces four dimensional analyses, each with **exactly two paragraphs and four recommendations**;
- validates structured output with Pydantic;
- exports a Word report.

## Models

- LLM: `gemini-3.6-flash`
- Embeddings: `models/gemini-embedding-001`

The Gemini 3.6 Flash client does not send `temperature`, `top_p`, or `top_k`.

## Web validation principles

Web information is complementary and cannot recalculate or replace spreadsheet maturity scores. The pipeline verifies municipality/UF identity, uses the IBGE code when available, prioritizes institutional sources, and distinguishes planned, contracted, ongoing, and completed actions.

## Installation

Python 3.10+ is required.

```bash
pip install -r requirements.txt
```

Set `GOOGLE_API_KEY` or `GEMINI_API_KEY`. Set `MUNICIPIO_DADOS_DIR` to the directory containing `indicadores.xlsx` if needed.

## Python usage

```python
from municipio_analise import Config, PipelineAnaliseMunicipio

config = Config(base_path="/path/to/data")
pipeline = PipelineAnaliseMunicipio(config)
pipeline.carregar_planilha()

report = pipeline.analisar_municipio("Viçosa")
path = pipeline.salvar_relatorio("Viçosa", report)
print(path)
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

GitHub Actions runs compilation and tests on Python 3.10, 3.11, and 3.12.

## Licensing

No reuse license is included in this package. Licensing should follow the responsible institution's guidance.
