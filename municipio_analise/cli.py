from __future__ import annotations

import argparse
import json

from .config import Config
from .pipeline import PipelineAnaliseMunicipio


def main():
    parser = argparse.ArgumentParser(description="Diagnóstico municipal com IA")
    parser.add_argument("--base-path", default=None, help="Pasta que contém indicadores.xlsx")
    parser.add_argument("--municipio", default=None, help="Município a analisar")
    parser.add_argument("--json", action="store_true", help="Imprime o JSON final")
    args = parser.parse_args()

    config = Config(base_path=args.base_path) if args.base_path else Config()
    pipeline = PipelineAnaliseMunicipio(config)
    pipeline.carregar_planilha()

    municipio = args.municipio
    if not municipio:
        municipios = pipeline.municipios()
        print("Municípios disponíveis:")
        for i, nome in enumerate(municipios, 1):
            print(f"{i} - {nome}")
        escolha = int(input("Digite o número do município: "))
        municipio = municipios[escolha - 1]

    relatorio = pipeline.analisar_municipio(municipio)
    caminho = pipeline.salvar_relatorio(municipio, relatorio)
    if args.json:
        print(json.dumps(relatorio, ensure_ascii=False, indent=2))
    print(f"Relatório gerado: {caminho}")


if __name__ == "__main__":
    main()
