# =====================================================
# FUNÇÕES AUXILIARES
# =====================================================
import unicodedata


def classificar_porte(populacao):
    if populacao <= 50000:
        return "pequeno porte"
    elif populacao <= 300000:
        return "médio porte"
    else:
        return "grande porte"


def normalizar(texto):
    """Remove espaços nas pontas, acentos e caixa — usada tanto para
    comparar palavras-chave quanto para casar nomes de colunas da planilha
    com as chaves dos mapas de classificação."""
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    return texto.encode("ascii", errors="ignore").decode("utf-8")
