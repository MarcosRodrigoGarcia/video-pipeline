"""Estructurador: lee la transcripción, genera el documento y los metadatos."""

import json
import re
import time
from pathlib import Path
from .llm_client import query_ollama
from .prompts import get_prompt


def summarize(
    transcription_path: str,
    output_md_path: str,
    output_sections_path: str,
    doc_type: str = "meeting_notes",
    model: str = "mistral:latest",
    context: str = "",
) -> dict:
    """
    Lee una transcripción JSON y genera un documento Markdown estructurado.
    
    Args:
        transcription_path: Ruta al JSON de transcripción (salida del Bloque 1).
        output_md_path: Ruta donde guardar el Markdown generado.
        output_sections_path: Ruta donde guardar el JSON de secciones.
        doc_type: Tipo de documento (meeting_notes, summary, tutorial).
        model: Modelo de Ollama a usar.
    
    Returns:
        Diccionario con metadatos del documento generado.
    """
    # Leer transcripción
    with open(transcription_path, "r", encoding="utf-8") as f:
        transcription = json.load(f)

    full_text = transcription["full_text"]
    segments = transcription["segments"]

    duration_seconds = segments[-1]["end"] if segments else 0
    duration_minutes = duration_seconds / 60
    min_words = max(250, round(duration_minutes / 10) * 250)

    print(f"Transcripción cargada: {len(segments)} segmentos, {len(full_text)} caracteres")
    print(f"Duración: {round(duration_minutes)}min → mínimo {min_words} palabras")
    print(f"Tipo de documento: {doc_type}")
    print(f"Modelo: {model}")
    print(f"Enviando a Ollama...")

    # Generar prompt y enviar al LLM
    prompt = get_prompt(doc_type, full_text, context, min_words=min_words)
    start_time = time.time()
    markdown = query_ollama(prompt, model=model)
    elapsed = round(time.time() - start_time, 1)

    print(f"Respuesta recibida en {elapsed}s")

    # Extraer secciones del Markdown generado
    sections = extract_sections(markdown, segments)

    # Guardar Markdown
    Path(output_md_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    # Guardar metadatos de secciones
    sections_data = {
        "title": sections[0]["title"] if sections else "Sin título",
        "type": doc_type,
        "model": model,
        "processing_time_seconds": elapsed,
        "sections": sections,
    }

    with open(output_sections_path, "w", encoding="utf-8") as f:
        json.dump(sections_data, f, ensure_ascii=False, indent=2)

    print(f"Documento guardado: {output_md_path}")
    print(f"Secciones guardadas: {output_sections_path}")
    print(f"Secciones encontradas: {len(sections)}")

    return sections_data


def extract_sections(markdown: str, segments: list) -> list:
    """
    Extrae las secciones del Markdown y les asigna timestamps aproximados.
    
    Divide el rango de tiempo total del vídeo entre las secciones
    de forma proporcional. En la v2 esto se puede mejorar con
    búsqueda semántica en los segmentos.
    """
    sections = []
    
    # Buscar todos los encabezados (# y ##)
    headings = re.findall(r'^(#{1,3})\s+(.+)$', markdown, re.MULTILINE)

    if not headings or not segments:
        return sections

    total_duration = segments[-1]["end"] if segments else 0
    section_duration = total_duration / max(len(headings), 1)

    for i, (level, title) in enumerate(headings):
        start_time = round(i * section_duration, 1)
        end_time = round((i + 1) * section_duration, 1)

        sections.append({
            "id": f"sec_{i:02d}",
            "title": title.strip(),
            "level": len(level),
            "start_time": start_time,
            "end_time": min(end_time, total_duration),
            "image_hint": "frame_at_start",
        })

    return sections