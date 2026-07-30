[English](README.md) | [Português](README.pt-BR.md)

# Municipal AI Diagnosis

A system for automatically generating institutional diagnostic reports for
Brazilian municipalities using Large Language Models (LLMs),
Retrieval-Augmented Generation (RAG), and semantic embeddings. The project
combines public indicators with the *Carta Brasileira para Cidades
Inteligentes* ("Brazilian Charter for Smart Cities" — the reference
framework published by the Brazilian federal government to guide municipal
digital-transformation policy) to produce structured technical analyses in
Word format.

## Key features

- Automatic analysis of municipal indicators
- Semantic classification using embeddings
- Contextual search with FAISS
- RAG using LangChain
- Institutional report generation with Gemini
- Automatic export to Microsoft Word

## Architecture

The processing pipeline follows the steps below:

```
Municipal indicators
      │
      ▼
Data normalization
      │
      ▼
Classification and embedding generation
      │
      ▼
FAISS vector index
      │
      ▼
Context retrieval (RAG)
      │
      ▼
Google Gemini
      │
      ▼
Structured JSON (Pydantic)
      │
      ▼
Institutional report (.docx)
```

## Project structure

```
municipio_analise/
    main.py            # entry point (main execution)
    config.py          # configuration (paths, API key, model)
    utils.py           # helper functions (normalization, size classification)
    dados_carta.py     # loading of the Carta Brasileira chunks
    classificacao.py   # dimension/topic taxonomy and indicator classification
    rag.py             # LLM, embeddings, and FAISS indices
    modelos.py         # Pydantic models for structured output
    prompts.py         # prompt templates and chain assembly
    analise.py         # model calls (with validation and retries)
    relatorio.py       # Word report generation
    data/              # project support data (Carta chunks, classification maps)
dados/                 # user input data (not versioned, see below)
requirements.txt
.gitignore
```

The original notebook (`Analise_municipio_langchain_com_embeddings.ipynb`)
is kept only as a demonstration. The modularized version above represents
the structure used in production.

Note: `municipio_analise` (Portuguese for "municipality analysis") and
`dados` (Portuguese for "data") are the actual package/folder names in this
repository and are left untranslated, since renaming them would break the
project's file paths and imports.

## Configuration

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure the Gemini API

**Linux/Mac:**

```bash
export GOOGLE_API_KEY="YOUR_KEY"
```

**Windows PowerShell:**

```powershell
$env:GOOGLE_API_KEY="YOUR_KEY"
```

**`.env` file:**

```
GOOGLE_API_KEY=YOUR_KEY
```

The `.env` file and the `dados/` folder must not be versioned (both are
already listed in `.gitignore`).

### 3. Prepare the data folder

Create a `dados/` folder at the project root and place inside it:

- `indicadores.xlsx` — a spreadsheet with one row per municipality,
  containing the municipality name column, the estimated total population,
  and the sectoral indicator columns.

Generated reports (`Relatorio_<municipio>.docx`) and the FAISS indices
(`faiss_index_topicos/`, `faiss_index_chunks/`) are also saved in this same
folder.

To use a different path, set the `MUNICIPIO_DADOS_DIR` environment
variable to the desired folder.

## How to run

```bash
python -m municipio_analise.main
```

The script lists the municipalities available in the spreadsheet, prompts
you to choose one, and generates the corresponding institutional report in
`dados/`.

## How the RAG works

- The text of the *Carta Brasileira para Cidades Inteligentes* is split
  into small chunks.
- Each chunk is converted into an embedding.
- The embeddings are stored in FAISS vector indices.
- For each municipality, the system retrieves only the most relevant
  chunks.
- Gemini uses the retrieved context together with the municipal indicators
  to produce a well-grounded technical report.

## Example output

The report is generated as a `.docx` file organized into sections by
analysis dimension. Below is a summarized, anonymized excerpt (fictitious
data) from the "General Analysis" section:

> **Institutional Report — Model Municipality**
>
> The municipality shows a solid foundation in essential urban services,
> with high coverage of water supply, sanitary sewage, and waste
> collection, including the implementation of selective collection.
> Educational infrastructure also stands out, evidenced by broad internet
> connectivity in public schools [...]
>
> Despite these advances, significant challenges remain in modernizing
> management and integrating technologies to optimize urban services
> [...]

The full example report (covering all dimensions — Economic,
Sociocultural, Environmental, and Institutional Capacity — along with the
corresponding improvement suggestions) is available as a sample file at
[`docs/Relatorio_Exemplo.docx`](docs/Relatorio_Exemplo.docx).

## Technologies

- Python
- LangChain
- Google Gemini
- FAISS
- Pandas
- Pydantic
- python-docx
- OpenPyXL

## Demo

![Example of a generated report](docs/relatorio-exemplo.png)

## Author

Developed by Rafael Augusto do Nascimento, as part of the activities of the
*Programa Cidades do Futuro* ("Cities of the Future Program"), an
initiative of the *Secretaria de Estado de Desenvolvimento Econômico de
Minas Gerais* (Minas Gerais State Secretariat of Economic Development,
Brazil).

- GitHub: [@Rafael-an144](https://github.com/Rafael-an144)

## Usage and licensing

This project was developed in the context of the *Programa Cidades do
Futuro*. Terms of use, reproduction, and distribution must follow the
guidelines of the responsible institution.
