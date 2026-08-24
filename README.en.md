# Smart City Diagnostic AI

[Versão em português](README.md)

Municipal diagnostic pipeline for the **Cidades do Futuro Program**, built around municipal maturity indicators, the Brazilian Charter for Smart Cities, semantic search with FAISS, and controlled web validation.

> Synchronized reference implementation: `notebooks/notebook_fonte_validacao_web.ipynb`

## What the project does

- reads `indicadores.xlsx`;
- classifies indicators into four dimensions and thematic topics;
- uses the 0-7 maturity scale to prioritize gaps and existing capacities;
- uses embeddings and FAISS as a semantic fallback for newly added indicators;
- uses a granular FAISS index of the Brazilian Charter for Smart Cities to retrieve relevant methodological references;
- prioritizes up to 5 indicators/topics per dimension for RAG;
- retrieves up to 8 candidates per priority and applies reranking;
- sends at most 8 final Charter chunks to the language model;
- uses contextual data only to characterize the municipality;
- generates the first draft of each dimension without web search;
- uses Claude Web Search to validate and update up to 5 priority points per dimension;
- revises each dimension using only reliable and territorially confirmed external facts;
- keeps the spreadsheet as the primary source: web search does not recalculate or replace maturity levels;
- generates 2 or 3 paragraphs per dimension and exactly 4 improvement recommendations;
- generates the General Analysis only after all four dimensions have been finalized;
- validates structured output with Pydantic;
- generates a Word report.

## Models

- **Main LLM:** Claude Sonnet 4.6 (`claude-sonnet-4-6`)
- **Web search:** Claude Web Search (`web_search_20250305`)
- **Embeddings:** Google Gemini (`models/gemini-embedding-001`)
- **Vector search:** FAISS

Gemini is kept only in the embeddings layer. Text generation, revision, and web search are handled by Claude.

## Current pipeline

```text
indicadores.xlsx
      ↓
spreadsheet normalization and indicator classification
      ↓
0-7 maturity levels
      ↓
selection of up to 5 priorities per dimension
      ↓
granular FAISS index of the Brazilian Charter for Smart Cities
      ↓
8 candidates per priority
      ↓
semantic + maturity + dimension + topic + coverage reranking
      ↓
up to 8 final Charter chunks
      ↓
Claude Sonnet: first draft WITHOUT web search
      ↓
Claude Web Search: validation of up to 5 priority points
      ↓
Claude Sonnet: final revision of the dimension
      ↓
repeat for all 4 dimensions
      ↓
General Analysis built from the finalized dimensions, with no new web search
      ↓
Word report
```

## How FAISS is used

FAISS is not used as the municipality's current-data database. It serves three distinct purposes:

1. **Semantic indicator classification:** when an indicator does not match an exact mapping or keyword rule, the system searches for the semantically closest topic.
2. **RAG over the Brazilian Charter for Smart Cities:** retrieves methodological excerpts that are useful for interpreting municipal priorities.
3. **Legacy-index fallback:** the previous chunk-selection logic remains available as a safety fallback if the granular index does not return relevant content.

The municipal database is dynamic and comes from the spreadsheet. The Charter/FAISS layer acts as a relatively stable methodological reference. Web search provides the current factual-update layer.

## Granular RAG and reranking

For each dimension:

1. indicators are grouped by topic;
2. the system prioritizes up to 5 topics/indicators based on maturity;
3. for each priority, it creates a query containing the dimension, topic, indicator, and observed municipal situation;
4. FAISS retrieves up to 8 candidates;
5. candidates are reranked using semantic similarity, indicator maturity, dimension match, topic match, and coverage across multiple indicators;
6. at most 8 chunks are sent to Claude.

The versioned granular corpus contains **185 documents**: 3 concepts, 5 principles, 6 guidelines, 8 strategic-objective contexts, and 163 recommendations from the revised edition of the Charter.

## Web validation

Web search is complementary and follows strict rules:

- confirm municipality and state before using an external fact;
- use the IBGE municipality code as an additional territorial check when available;
- prioritize city halls, public agencies, government institutions, universities, and other official sources;
- distinguish between planned, contracted, under-implementation, and completed actions;
- never replace or recalculate spreadsheet indicators;
- never claim the spreadsheet is wrong only because an external source uses a different period or methodology;
- avoid recommending as new an action that is already demonstrably underway;
- never create a recommendation based only on a news article;
- never use the Cidades do Futuro Program itself as evidence supporting the diagnosis.

Validation runs **after the first draft**, once per dimension, covering up to five priority points plus complementary nominal enrichment. If no reliable update is found, the draft is preserved.

## Language and editorial rules

Reports are written for municipal managers who are not technical specialists. The system prioritizes direct sentences, explains acronyms and concepts when needed, and avoids unnecessary jargon.

Additional rules:

- do not use the Cidades do Futuro Program as diagnostic evidence or as a recommendation;
- do not use em dashes (`—`) in the final report;
- use 2 or 3 paragraphs per dimension;
- produce exactly 4 improvement recommendations per dimension;
- preserve the historical indicator even when web search finds a newer ongoing action.

## Local package installation

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Configure environment variables:

```text
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
MUNICIPIO_DADOS_DIR=./dados
```

- `ANTHROPIC_API_KEY`: generation, revision, and Claude Web Search;
- `GEMINI_API_KEY`: embeddings/FAISS only.

Never publish API keys on GitHub.

Place `indicadores.xlsx` in the directory configured by `MUNICIPIO_DADOS_DIR`.

### Run locally

```bash
python -m municipio_analise "Viçosa"
```

or, after installing the package:

```bash
smart-city-diagnostic "Viçosa"
```

To skip Word generation:

```bash
python -m municipio_analise "Viçosa" --sem-word
```

On the first granular-RAG run, the Charter index is built in batches and stored locally. A manifest allows an interrupted build to resume. Generated FAISS indexes must not be committed.

## Running in Google Colab

The reference notebook remains available for Google Colab and uses Google Drive for reading the spreadsheet, persisting FAISS indexes, and saving reports.

Open:

`notebooks/notebook_fonte_validacao_web.ipynb`

In Colab, configure the notebook Secrets:

- `ANTHROPIC_API_KEY`;
- `API` for Gemini embeddings.

## Repository structure

```text
smart-city-diagnostic-ai/
├── dados/
├── docs/
├── municipio_analise/
│   ├── data/
│   │   └── carta_revisada_snapshot.json
│   ├── carta_granular.py
│   ├── llm_service.py
│   ├── pipeline.py
│   └── ...
├── notebooks/
│   ├── exemplo_colab.ipynb
│   └── notebook_fonte_validacao_web.ipynb
├── tests/
├── CHANGELOG.md
├── README.en.md
├── README.md
├── requirements-dev.txt
├── requirements.txt
└── pyproject.toml
```

### Status of `municipio_analise/`

Starting with version **0.3.0**, the modular package is synchronized with the reference notebook architecture: Claude Sonnet 4.6, post-draft Claude Web Search, granular Charter RAG, and the General Analysis generated only after all four dimensions are finalized.

## Security and data

- never publish `.env`, API keys, municipal spreadsheets, generated FAISS indexes, or operational reports;
- never publish `ANTHROPIC_API_KEY` or the Gemini API key;
- keep operational data and generated artifacts in `.gitignore`.

## Licensing

Check the repository license and the project's institutional rules before reusing or redistributing components.
