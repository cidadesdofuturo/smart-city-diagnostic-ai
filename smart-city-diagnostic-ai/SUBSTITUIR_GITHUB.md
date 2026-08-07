# Como substituir manualmente o conteúdo no GitHub

Este procedimento não exige PowerShell nem Git instalado no computador.

## 1. Baixe e extraia o ZIP

Extraia o pacote e abra a pasta `smart-city-diagnostic-ai`.

## 2. Apague os arquivos antigos pelo navegador

No repositório atual do GitHub, remova os arquivos e pastas da versão anterior. Não exclua o repositório em **Settings > Danger Zone**.

## 3. Faça o upload da nova estrutura

Na raiz do repositório:

1. clique em **Add file**;
2. escolha **Upload files**;
3. arraste o conteúdo da pasta extraída para a página;
4. confira se as pastas `.github`, `municipio_analise`, `notebooks`, `tests`, `docs` e `dados` aparecem na estrutura do upload;
5. faça o commit diretamente na branch `main`.

Importante: suba o **conteúdo** da pasta, não o arquivo ZIP e não uma pasta extra envolvendo todo o projeto.

## 4. Não envie dados privados

Não envie:

- `.env`;
- `indicadores.xlsx` real;
- chaves de API;
- `faiss_index_topicos/`;
- `faiss_index_chunks/`;
- relatórios `.docx` gerados localmente.

## 5. Confira a raiz

A raiz deve conter, entre outros:

```text
.github/
dados/
docs/
municipio_analise/
notebooks/
tests/
.gitignore
README.md
README.en.md
CHANGELOG.md
pyproject.toml
requirements.txt
requirements-dev.txt
```

## 6. Confira o workflow

Depois do commit, abra a aba **Actions**. O workflow de testes deve executar automaticamente.
