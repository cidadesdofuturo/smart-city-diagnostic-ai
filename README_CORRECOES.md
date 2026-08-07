# Correções geradas a partir do notebook

Este pacote contém os arquivos que devem substituir/adicionar no repositório `smart-city-diagnostic-ai`.

## Arquivos corrigidos
- `config.py`: reconcilia a configuração modular com o notebook e usa `temperature=0.2`.
- `prompts.py`: preserva os prompts multilinha do notebook e restaura `criar_chains()`.
- `rag.py`: passa a ler a configuração central corretamente.
- `analise.py`: volta a enviar `dados_contextuais_txt` para os prompts.
- `contexto.py`: novo módulo com os dados contextuais existentes no notebook.
- `relatorio.py`: corrige tratamento de caminhos com `pathlib.Path`.
- `main.py`: restaura o fluxo completo do notebook na arquitetura modular.
- `requirements.txt`: inclui `openpyxl`, necessário para `.xlsx`.

## Antes de executar
Defina a chave:

```bash
export GOOGLE_API_KEY=...
```

No Windows PowerShell:

```powershell
$env:GOOGLE_API_KEY="..."
```

Opcionalmente defina a pasta da planilha e dos índices:

```bash
export MUNICIPIO_DADOS_DIR=/caminho/para/dados
```

Depois execute a partir da raiz do repositório:

```bash
python -m municipio_analise.main
```
