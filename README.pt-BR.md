[English](README.md) | [Português](README.pt-BR.md)

# Municipal AI Diagnosis

Sistema para geração automática de relatórios institucionais de municípios
utilizando Large Language Models (LLMs), Retrieval-Augmented Generation
(RAG) e embeddings semânticos. O projeto combina indicadores públicos com
a Carta Brasileira para Cidades Inteligentes para produzir análises
técnicas estruturadas em formato Word.

## Principais funcionalidades

- Análise automática de indicadores municipais
- Classificação semântica utilizando embeddings
- Busca contextual com FAISS
- RAG utilizando LangChain
- Geração de relatórios institucionais com Gemini
- Exportação automática para Microsoft Word

## Arquitetura

O fluxo de processamento segue as etapas abaixo:

```
Indicadores municipais
      │
      ▼
Normalização dos dados
      │
      ▼
Classificação e geração de embeddings
      │
      ▼
Índice vetorial FAISS
      │
      ▼
Recuperação de contexto (RAG)
      │
      ▼
Google Gemini
      │
      ▼
JSON estruturado (Pydantic)
      │
      ▼
Relatório institucional (.docx)
```

## Estrutura do projeto

```
municipio_analise/
    main.py            # ponto de entrada (execução principal)
    config.py          # configurações (caminhos, chave de API, modelo)
    utils.py           # funções auxiliares (normalização, porte)
    dados_carta.py     # carregamento dos chunks da Carta Brasileira
    classificacao.py   # taxonomia de dimensões/tópicos e classificação de indicadores
    rag.py             # LLM, embeddings e índices FAISS
    modelos.py         # modelos Pydantic de saída estruturada
    prompts.py         # templates de prompt e montagem das chains
    analise.py         # chamadas ao modelo (com validação e retentativas)
    relatorio.py       # geração do relatório em Word
    data/              # dados de apoio do projeto (chunks da Carta, mapas de classificação)
dados/                 # dados de entrada do usuário (não versionado, ver abaixo)
requirements.txt
.gitignore
```

O notebook original (`Analise_municipio_langchain_com_embeddings.ipynb`) é
mantido apenas como demonstração. A versão modularizada acima representa
a estrutura utilizada em produção.

## Configuração

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar a API do Gemini

**Linux/Mac:**

```bash
export GOOGLE_API_KEY="SUA_CHAVE"
```

**Windows PowerShell:**

```powershell
$env:GOOGLE_API_KEY="SUA_CHAVE"
```

**Arquivo `.env`:**

```
GOOGLE_API_KEY=SUA_CHAVE
```

O arquivo `.env` e a pasta `dados/` não devem ser versionados (ambos já
constam no `.gitignore`).

### 3. Preparar a pasta de dados

Crie uma pasta `dados/` na raiz do projeto e coloque nela:

- `indicadores.xlsx` — planilha com uma linha por município, contendo a
  coluna de nome do município, a população total estimada e as colunas de
  indicadores setoriais.

Os relatórios gerados (`Relatorio_<municipio>.docx`) e os índices FAISS
(`faiss_index_topicos/`, `faiss_index_chunks/`) também são salvos nessa
mesma pasta.

Se quiser usar outro caminho, defina a variável de ambiente
`MUNICIPIO_DADOS_DIR` apontando para a pasta desejada.

## Como executar

```bash
python -m municipio_analise.main
```

O script lista os municípios disponíveis na planilha, pede para escolher
um deles e gera o relatório institucional correspondente em `dados/`.

## Como funciona o RAG

- Os textos da Carta Brasileira para Cidades Inteligentes são divididos
  em pequenos trechos.
- Cada trecho é convertido em um embedding.
- Os embeddings são armazenados em índices vetoriais FAISS.
- Para cada município, o sistema recupera apenas os trechos mais
  relevantes.
- O Gemini utiliza o contexto recuperado e os indicadores municipais para
  produzir um relatório técnico fundamentado.

## Exemplo de saída

O relatório é gerado em `.docx` e organizado em seções por dimensão de
análise. Abaixo, um trecho resumido e anonimizado (dados fictícios) da
seção "Análise Geral":

> **Relatório Institucional — Município Modelo**
>
> O município demonstra um sólido fundamento em serviços urbanos
> essenciais, com alta cobertura de abastecimento de água, esgotamento
> sanitário e coleta de resíduos, incluindo a implementação de coleta
> seletiva. A infraestrutura educacional também se destaca, evidenciada
> pela ampla conectividade à internet nas escolas públicas [...]
>
> Apesar dos avanços, persistem desafios significativos na modernização
> da gestão e na integração de tecnologias para otimizar os serviços
> urbanos [...]

O relatório completo (com todas as dimensões — Econômica, Sociocultural,
Meio Ambiente e Capacidades Institucionais — e as respectivas sugestões
de melhoria) está disponível como exemplo em
[`docs/Relatorio_Exemplo.docx`](docs/Relatorio_Exemplo.docx).

## Tecnologias

- Python
- LangChain
- Google Gemini
- FAISS
- Pandas
- Pydantic
- python-docx
- OpenPyXL

## Demonstração

![Exemplo de relatório gerado](docs/relatorio-exemplo.png)

## Autor

Desenvolvido por Rafael Augusto do Nascimento, no contexto das atividades
do Programa Cidades do Futuro, da Secretaria de Estado de Desenvolvimento
Econômico de Minas Gerais.

- GitHub: [@Rafael-an144](https://github.com/Rafael-an144)

## Uso e licenciamento

Projeto desenvolvido no contexto do Programa Cidades do Futuro. As
condições de uso, reprodução e distribuição devem observar as orientações
da instituição responsável.
