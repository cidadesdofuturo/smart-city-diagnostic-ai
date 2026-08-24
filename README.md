# Smart City Diagnostic AI

Pipeline de diagnóstico municipal do Programa Cidades do Futuro, estruturado a partir de indicadores municipais de maturidade, da Carta Brasileira para Cidades Inteligentes, busca semântica com FAISS e validação web controlada.

> Implementação de referência sincronizada: `notebooks/notebook_fonte_validacao_web.ipynb`

## O que o projeto faz

- lê `indicadores.xlsx`;
- classifica indicadores em quatro dimensões e tópicos;
- usa a escala de maturidade 0–7 para priorizar lacunas e capacidades;
- usa embeddings e FAISS para classificação semântica de indicadores novos;
- usa um índice FAISS granular da Carta Brasileira para recuperar referências metodológicas relevantes;
- prioriza até 5 indicadores/tópicos por dimensão para o RAG;
- recupera até 8 candidatos por indicador e aplica reranking;
- envia no máximo 8 chunks finais da Carta ao modelo;
- usa dados contextuais apenas para caracterização do município;
- gera o primeiro rascunho da dimensão sem pesquisa web;
- usa Claude Web Search para validar e atualizar até 5 pontos prioritários por dimensão;
- revisa a dimensão com base apenas em fatos externos confiáveis e territorialmente confirmados;
- mantém a planilha como fonte principal: a web não recalcula nem substitui os níveis de maturidade;
- gera 2 ou 3 parágrafos por dimensão e 4 sugestões de melhoria;
- gera a Análise Geral somente depois das quatro dimensões finalizadas;
- valida a saída estruturada com Pydantic;
- gera relatório Word.

## Modelos

- LLM principal: Claude Sonnet 4.6 (`claude-sonnet-4-6`)
- Pesquisa web: Claude Web Search (`web_search_20250305`)
- Embeddings: Google Gemini (`models/gemini-embedding-001`)
- Busca vetorial: FAISS

O Gemini permanece apenas na camada de embeddings. A geração, revisão e pesquisa web são feitas pelo Claude.

## Fluxo atual

```text
indicadores.xlsx
      ↓
normalização e classificação dos indicadores
      ↓
níveis de maturidade 0–7
      ↓
seleção de até 5 prioridades por dimensão
      ↓
FAISS granular da Carta Brasileira
      ↓
8 candidatos por prioridade
      ↓
reranking semântico + maturidade + dimensão + tópico + cobertura
      ↓
até 8 chunks finais da Carta
      ↓
Claude Sonnet: rascunho da dimensão SEM web
      ↓
Claude Web Search: validação de até 5 pontos
      ↓
Claude Sonnet: revisão final da dimensão
      ↓
repete para as 4 dimensões
      ↓
Análise Geral a partir das dimensões finalizadas, sem nova web
      ↓
relatório Word
```

## Como o FAISS é usado

O FAISS não é usado como base de dados atual do município. Ele cumpre três funções:

1. **Classificação semântica de indicadores:** quando um indicador não encontra correspondência exata ou por palavra-chave, o sistema procura o tópico semanticamente mais próximo.
2. **RAG da Carta Brasileira:** recupera trechos metodológicos relevantes para interpretar as prioridades do município.
3. **Fallback do índice antigo:** a lógica anterior de chunks permanece como segurança caso o índice granular não retorne conteúdo.

A base municipal é dinâmica e vem da planilha. A Carta/FAISS funciona como referência metodológica relativamente estável. A pesquisa web funciona como camada de atualização factual.

## RAG granular e reranking

Para cada dimensão:

1. os indicadores são agrupados por tópico;
2. o sistema prioriza até 5 tópicos/indicadores com base na maturidade;
3. para cada prioridade, cria uma consulta com dimensão, tópico, indicador e situação observada;
4. o FAISS recupera até 8 candidatos;
5. os candidatos são reranqueados considerando similaridade semântica, maturidade do indicador, aderência à dimensão, aderência ao tópico e cobertura de múltiplos indicadores;
6. no máximo 8 chunks são enviados ao Claude.

O corpus granular versionado contém **185 documentos**: 3 conceitos, 5 princípios, 6 diretrizes, 8 contextos de objetivos e 163 recomendações da edição revisada da Carta.

## Validação web

A pesquisa web é complementar e segue regras rígidas:

- confirmar município e UF antes de usar um fato;
- usar código IBGE como conferência adicional quando disponível;
- priorizar Prefeitura, autarquias, governos, universidades e instituições públicas;
- diferenciar ação planejada, contratada, em implantação e concluída;
- não substituir nem recalcular indicadores da planilha;
- não declarar que a planilha está errada apenas porque uma fonte externa usa outro período ou metodologia;
- evitar recomendar como nova uma ação que já esteja comprovadamente em execução;
- não gerar recomendação baseada somente em uma notícia;
- não citar o próprio Programa Cidades do Futuro como evidência do diagnóstico.

A validação é feita **depois do rascunho**, em uma única etapa de grounding por dimensão, com até cinco pontos prioritários e enriquecimento nominal complementar. Se não houver atualização confiável, o rascunho é mantido.

## Linguagem e regras editoriais

Os relatórios são escritos para gestores municipais não especialistas. O sistema prioriza frases diretas, explica siglas e conceitos quando necessário e evita jargão excessivo.

Regras adicionais:

- não usar o Programa Cidades do Futuro como evidência ou recomendação;
- não usar travessão (`—`) no texto final;
- usar 2 ou 3 parágrafos por dimensão;
- produzir exatamente 4 sugestões de melhoria por dimensão;
- preservar o indicador histórico mesmo quando a web mostra uma ação mais recente.

## Instalação do pacote modular

Requer Python 3.11+.

```bash
python -m venv .venv
```

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

Configure as chaves no ambiente:

```text
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
MUNICIPIO_DADOS_DIR=./dados
```

- `ANTHROPIC_API_KEY`: geração, revisão e Claude Web Search;
- `GEMINI_API_KEY`: somente embeddings/FAISS.

Nunca publique as chaves no GitHub.

Coloque `indicadores.xlsx` no diretório definido por `MUNICIPIO_DADOS_DIR`.

### Execução local

```bash
python -m municipio_analise "Viçosa"
```

ou, após instalar o pacote:

```bash
smart-city-diagnostic "Viçosa"
```

Para não gerar Word:

```bash
python -m municipio_analise "Viçosa" --sem-word
```

Na primeira execução do RAG granular, o índice da Carta é construído em lotes e salvo localmente. O manifesto permite retomar uma construção interrompida. Índices FAISS não devem ser versionados.

## Execução no Colab

O notebook continua disponível para execução no Google Colab e usa o Google Drive para leitura da planilha, persistência dos índices FAISS e gravação dos relatórios.

Abra:

`notebooks/notebook_fonte_validacao_web.ipynb`

No Colab, configure os Secrets usados no notebook:

- `ANTHROPIC_API_KEY`;
- `API` para embeddings Gemini.

## Estrutura do repositório

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

### Estado do pacote `municipio_analise/`

A partir da versão **0.3.0**, o pacote modular foi sincronizado com a arquitetura do notebook-fonte: Claude Sonnet 4.6, Claude Web Search pós-rascunho, RAG granular da Carta e Análise Geral ao final.

## Segurança e dados

- nunca publique `.env`, planilhas municipais, índices FAISS gerados ou relatórios contendo dados de trabalho;
- nunca publique `ANTHROPIC_API_KEY` ou a chave Gemini;
- mantenha dados operacionais e artefatos gerados no `.gitignore`.

## Licenciamento

Consulte o arquivo de licença e as regras institucionais do projeto antes de reutilizar ou redistribuir componentes.
