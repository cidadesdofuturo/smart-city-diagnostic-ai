# Smart City Diagnostic AI

[English version](README.en.md)

Pipeline de diagnóstico municipal do **Programa Cidades do Futuro**, estruturado a partir da Carta Brasileira para Cidades Inteligentes, indicadores municipais de maturidade e validação web controlada.

A implementação canônica é `Config + PipelineAnaliseMunicipio`. O notebook corrente com pesquisa web e validação por dimensão está preservado em [`notebooks/notebook_fonte_validacao_web.ipynb`](notebooks/notebook_fonte_validacao_web.ipynb).

## O que o projeto faz

- lê `indicadores.xlsx`;
- classifica indicadores em quatro dimensões e tópicos;
- usa escala de maturidade **0–7** para priorizar temas que demandam maior atenção;
- usa FAISS e embeddings para fallback semântico de classificação e recuperação de chunks;
- usa dados contextuais apenas para caracterização do cenário;
- usa **Google Search Grounding** para uma pesquisa geral breve do município;
- realiza uma validação web específica para cada dimensão, buscando fatos recentes que possam qualificar a leitura dos indicadores;
- mantém a planilha como fonte principal: a web não recalcula nem substitui os níveis de maturidade;
- gera uma análise geral em dois parágrafos;
- gera quatro análises dimensionais, cada uma com **exatamente dois parágrafos e quatro sugestões**;
- valida a saída estruturada com Pydantic;
- gera relatório Word.

## Modelos

- LLM: `gemini-3.6-flash`
- Embeddings: `models/gemini-embedding-001`

Para o Gemini 3.6 Flash, o código não envia `temperature`, `top_p` ou `top_k`.

## Fluxo

```text
indicadores.xlsx
      ↓
normalização da planilha
      ↓
classificação dos indicadores
      ↓
maturidade 0–7
      ↓
seleção de chunks da Carta / FAISS
      ↓
dados contextuais
      ↓
pesquisa web geral do município
      ↓
análise geral estruturada
      ↓
para cada dimensão:
  pesquisa web de validação
        ↓
  análise em 2 parágrafos
        ↓
  4 sugestões
      ↓
relatório Word
```

Em uma execução completa podem ocorrer até **10 chamadas ao modelo**: uma pesquisa web geral, uma análise geral, quatro pesquisas web dimensionais e quatro análises dimensionais. Se a pesquisa web não retornar contexto confiável, a geração continua baseada na planilha e na base conceitual.

## Estrutura

```text
smart-city-diagnostic-ai/
├── municipio_analise/
│   ├── data/
│   │   ├── carta_chunks.json
│   │   ├── mapa_indicadores.json
│   │   ├── mapa_nivel_maturidade.json
│   │   ├── colunas_nao_indicadores.json
│   │   └── dados_contextuais.json
│   ├── classificador.py
│   ├── config.py
│   ├── contexto.py
│   ├── dados.py
│   ├── embeddings_service.py
│   ├── llm_service.py
│   ├── maturidade.py
│   ├── modelos.py
│   ├── pipeline.py
│   ├── planilha.py
│   ├── prompts.py
│   ├── relatorio.py
│   ├── seletor_chunks.py
│   ├── taxonomia.py
│   └── utils.py
├── notebooks/
│   ├── exemplo_colab.ipynb
│   └── notebook_fonte_validacao_web.ipynb
├── tests/
├── docs/
├── .github/workflows/tests.yml
├── .env.example
├── requirements.txt
└── pyproject.toml
```

## Instalação

Requer Python 3.10+.

```bash
pip install -r requirements.txt
```

Configure a chave usando `GOOGLE_API_KEY` ou `GEMINI_API_KEY`.

A pasta de dados pode ser definida por `MUNICIPIO_DADOS_DIR` e deve conter `indicadores.xlsx`. Os índices FAISS e relatórios também são persistidos nessa pasta.

## Uso em Python

```python
from municipio_analise import Config, PipelineAnaliseMunicipio

config = Config(base_path="/caminho/para/dados")
pipeline = PipelineAnaliseMunicipio(config)
pipeline.carregar_planilha()

relatorio = pipeline.analisar_municipio("Viçosa")
caminho = pipeline.salvar_relatorio("Viçosa", relatorio)
print(caminho)
```

## Uso por linha de comando

```bash
python -m municipio_analise --base-path "/caminho/para/dados"
```

Ou:

```bash
python -m municipio_analise --base-path "/caminho/para/dados" --municipio "Viçosa" --json
```

## Colab

- [`notebooks/exemplo_colab.ipynb`](notebooks/exemplo_colab.ipynb): interface enxuta para executar o pacote.
- [`notebooks/notebook_fonte_validacao_web.ipynb`](notebooks/notebook_fonte_validacao_web.ipynb): notebook corrente usado como fonte de verdade desta reconstrução.

## Maturidade 0–7

A fonte primária é a coluna `N M Indicador...` pareada a cada indicador. O fallback textual aceita:

| Nível | Interpretação textual de fallback |
|---:|---|
| 0 | inexistente / não / ausente |
| 1 | inicial |
| 2 | básico |
| 3 | em desenvolvimento |
| 4 | em implantação |
| 5 | intermediário |
| 6 | avançado |
| 7 | consolidado / sim |

Valores numéricos fora de 0–7 não são interpretados como maturidade pelo fallback.

## Validação web

A pesquisa web é complementar. As regras implementadas são:

- confirmar município e UF antes de usar um fato;
- usar o código IBGE como conferência adicional quando disponível;
- priorizar Prefeitura, órgãos oficiais, universidades e instituições públicas;
- diferenciar ação planejada, contratada, em implantação e concluída;
- não substituir nem recalcular indicadores da planilha;
- não declarar que a planilha está errada apenas porque uma fonte externa usa outro período ou metodologia;
- evitar recomendar como nova uma ação que já esteja comprovadamente em execução;
- não gerar sugestão baseada somente em uma notícia ou informação externa.

## Testes

```bash
pip install -r requirements-dev.txt
pytest -q
```

O GitHub Actions também executa compilação e testes em Python 3.10, 3.11 e 3.12.

## Segurança e dados

- `.env`, planilhas, índices FAISS e relatórios gerados estão no `.gitignore`.
- Nunca publique a chave da API.
- `allow_dangerous_deserialization=True` é usado apenas para índices FAISS locais previamente gerados pelo próprio projeto. Não carregue índices recebidos de fontes não confiáveis.

## Metodologia e arquitetura

- [Arquitetura](docs/ARQUITETURA.md)
- [Metodologia](docs/METODOLOGIA.md)

## Licenciamento

Este pacote não inclui uma licença de reutilização. A definição de licenciamento deve seguir as orientações da instituição responsável pelo repositório.
