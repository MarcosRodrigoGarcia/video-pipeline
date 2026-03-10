"""Script de prueba para el resumidor (Bloque 2)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.summarizer import summarize


def main():
    transcription = "workspace/transcriptions/video.json"
    output_md = "workspace/documents/video.md"
    output_sections = "workspace/documents/sections.json"

    print("=" * 50)
    print("BLOQUE 2: Generando documento estructurado...")
    print("=" * 50)

    result = summarize(
        transcription_path=transcription,
        output_md_path=output_md,
        output_sections_path=output_sections,
        doc_type="meeting_notes",
    )

    print("\n" + "=" * 50)
    print("RESUMEN")
    print("=" * 50)
    print(f"Título: {result['title']}")
    print(f"Secciones: {len(result['sections'])}")
    print(f"Tiempo de proceso: {result['processing_time_seconds']}s")
    
    # Mostrar el documento generado
    print("\n" + "=" * 50)
    print("DOCUMENTO GENERADO:")
    print("=" * 50)
    with open(output_md, "r", encoding="utf-8") as f:
        print(f.read())


if __name__ == "__main__":
    main()