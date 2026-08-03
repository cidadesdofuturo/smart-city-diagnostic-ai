# =====================================================
# CONFIGURAÇÕES
# =====================================================
"""Configurações do projeto.

Nenhum caminho pessoal ou chave de API fica gravado aqui: tudo vem de
variáveis de ambiente ou de uma pasta local relativa ao projeto, para que
qualquer pessoa consiga clonar o repositório e executar sem editar código.
"""

import os
from pathlib import Path

# Pasta local de dados (planilhas de entrada e relatórios gerados).
# Pode ser sobrescrita definindo a variável de ambiente MUNICIPIO_DADOS_DIR.
BASE_PATH = Path(os.getenv("MUNICIPIO_DADOS_DIR", "./dados"))

ARQUIVO_PLANILHA = BASE_PATH / "indicadores.xlsx"

COLUNA_MUNICIPIO = "municipio"
COLUNA_POPULACAO = "populacao total estimada do municipio"

# Chave da API do Google (Gemini). Defina no ambiente, por exemplo:
#   export GOOGLE_API_KEY="sua-chave-aqui"
# ou em um arquivo .env (veja o README para instruções).
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

MODELO = "gemini-2.5-flash"
MODELO_EMBEDDING = "models/gemini-embedding-001"

# Índices FAISS são persistidos localmente: gerados uma única vez e
# reaproveitados nas próximas execuções (evita reprocessar embeddings sempre).
FAISS_INDEX_TOPICOS_PATH = BASE_PATH / "faiss_index_topicos"
FAISS_INDEX_CHUNKS_PATH = BASE_PATH / "faiss_index_chunks"

# Limiar de relevância (0-1) usado no fallback semântico de classificação
# de indicadores por embeddings. Ajuste empiricamente conforme os resultados.
LIMIAR_RELEVANCIA_TOPICO = 0.75


def validar_configuracao():
    """Confere se a chave de API foi definida antes de qualquer chamada ao modelo."""
    if not GOOGLE_API_KEY:
        raise RuntimeError(
            "GOOGLE_API_KEY não definida. Configure a variável de ambiente "
            "antes de executar (veja o README)."
        )
