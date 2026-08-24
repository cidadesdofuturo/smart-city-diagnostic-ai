from __future__ import annotations

import argparse
import json
from .config import Config
from .pipeline import PipelineAnaliseMunicipio
from .planilha import carregar_planilha, listar_municipios


def main():
    parser = argparse.ArgumentParser(description="Diagnóstico municipal com Claude + RAG da Carta")
    parser.add_argument("municipio", nargs="?", help="Nome exato do município na planilha")
    parser.add_argument("--dados-dir", default=None, help="Diretório com indicadores.xlsx e índices FAISS")
    parser.add_argument("--sem-word", action="store_true", help="Não gerar relatório DOCX")
    args = parser.parse_args()
    cfg = Config(base_path=args.dados_dir) if args.dados_dir else Config()
    municipio = args.municipio
    if not municipio:
        df = carregar_planilha(cfg)
        municipios = listar_municipios(df, cfg.coluna_municipio)
        for i, nome in enumerate(municipios, 1):
            print(f"{i} - {nome}")
        escolha = int(input("Digite o número do município: "))
        municipio = municipios[escolha - 1]
    resultado = PipelineAnaliseMunicipio(cfg).analisar(municipio, gerar_word=not args.sem_word)
    print(json.dumps(resultado, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
