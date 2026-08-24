from __future__ import annotations

import re
from pathlib import Path
from docx import Document
from .utils import separar_paragrafos


def gerar_relatorio_word(municipio: str, relatorio: dict, output_dir: Path | str) -> Path:
    output_dir = Path(output_dir); output_dir.mkdir(parents=True, exist_ok=True)
    doc = Document()
    doc.add_heading(f"Relatório Institucional – {municipio}", level=1)
    doc.add_heading("Análise Geral", level=2)
    for p in separar_paragrafos(relatorio["analise_geral"]):
        doc.add_paragraph(p)
    nomes = {
        "economica": "Dimensão Econômica", "sociocultural": "Dimensão Sociocultural",
        "meio_ambiente": "Dimensão Meio Ambiente",
        "capacidades_institucionais": "Dimensão Capacidades Institucionais",
    }
    for chave, titulo in nomes.items():
        bloco = relatorio["dimensoes"][chave]
        doc.add_heading(titulo, level=2)
        for p in separar_paragrafos(bloco["analise"]):
            doc.add_paragraph(p)
        doc.add_paragraph("Sugestões de melhoria:")
        for sugestao in bloco["sugestoes"]:
            doc.add_paragraph(sugestao, style="List Bullet")
    seguro = re.sub(r"[^\w.-]+", "_", municipio, flags=re.UNICODE).strip("_")
    destino = output_dir / f"Relatorio_{seguro}.docx"
    doc.save(destino)
    return destino
