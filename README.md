# municipio_analise

Pipeline de análise institucional de municípios do programa **Cidades do Futuro** (GovTech/MG), refatorado em arquitetura modular orientada a objetos, com LangChain, Gemini, FAISS, chamadas assíncronas e testes automatizados.

## Atualização sincronizada com o notebook (agosto/2026)

A versão atual incorpora as alterações do notebook `Analise_municipio_langchain_com_embeddings`:

- `temperature=0.2`, `top_p=0.9` e `max_output_tokens=4096`;
- embeddings com `models/gemini-embedding-001`;
- índice FAISS de **tópicos** para fallback semântico na classificação de indicadores novos;
- índice FAISS de **chunks da Carta** para tópicos sem trecho dedicado, sempre restringindo a busca à mesma dimensão;
- persistência dos índices em `faiss_index_topicos/` e `faiss_index_chunks/` dentro de `BASE_PATH`;
- dados contextuais (PIB, IDH-M, GINI, CAPAG, ecossistema de TIC/PD&I e estrutura de TI) usados apenas para contextualizar a análise textual;
- prompts revisados para linguagem mais direta, factual e institucional, com menos formulações promocionais ou típicas de texto gerado por IA.

Os dados contextuais **não** entram no cálculo de maturidade, na classificação dos indicadores, na ordenação das prioridades ou como origem direta das sugestões.

## Estrutura

```text
municipio_analise/
├── __init__.py
├── config.py
├── exceptions.py
├── models.py
├── data/
│   ├── dimensoes.py
│   ├── carta_chunks.json
│   ├── topicos_sem_chunk.json
│   ├── indicadores_map.json
│   ├── nivel_maturidade_map.json
│   ├── colunas_nao_indicadores.json
│   └── dados_contextuais_map.json
├── carta.py
├── classificador.py
├── contexto.py
├── embeddings_service.py
├── maturidade.py
├── planilha.py
├── prompts.py
├── llm_service.py
├── relatorio.py
├── pipeline.py
├── tools.py
├── agent.py
├── main.py
├── main.ipynb
├── requirements.txt
└── tests/
```

## Como usar no Colab

O `main.ipynb` do repositório é um notebook enxuto que monta o Drive e chama o pacote modular. Coloque a chave Gemini em **Colab Secrets** com o nome `API` (o notebook também aceita `GOOGLE_API_KEY`).

```python
import asyncio
from municipio_analise import Config, PipelineAnaliseMunicipio

config = Config(base_path="/content/drive/MyDrive/Scripts/Analise de municipio")
pipeline = PipelineAnaliseMunicipio(config)
pipeline.carregar_planilha()

relatorio = await pipeline.analisar_municipio("Viçosa")
pipeline.salvar_relatorio(relatorio)
```

Na primeira execução, os índices FAISS são construídos com a API de embeddings e salvos em `BASE_PATH`. Nas próximas execuções, eles são carregados do Drive sem refazer todos os embeddings.

Para desativar temporariamente os fallbacks semânticos:

```python
config = Config(
    base_path="/content/drive/MyDrive/Scripts/Analise de municipio",
    usar_embeddings_semanticos=False,
)
```

## Agente conversacional

```python
from municipio_analise import AgenteAnaliseMunicipal

agente = AgenteAnaliseMunicipal(pipeline)
resposta = await agente.perguntar("Quais municípios estão disponíveis?")
print(resposta)
```

## Testes

```bash
pip install -r requirements.txt
pytest
```
