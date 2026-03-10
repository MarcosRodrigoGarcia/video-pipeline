"""Transcribe audio usando faster-whisper en GPU."""

import json
import time
from pathlib import Path
from faster_whisper import WhisperModel


def transcribe(audio_path: str, output_path: str, model_size: str = "large-v3-turbo") -> dict:
    """
    Transcribe un fichero de audio y genera JSON con timestamps.
    
    Args:
        audio_path: Ruta al fichero WAV.
        output_path: Ruta donde guardar el JSON de transcripción.
        model_size: Tamaño del modelo whisper (default: large-v3).
    
    Returns:
        Diccionario con la transcripción completa y segmentos.
    """
    print(f"Cargando modelo {model_size}...")
    start_time = time.time()

    model = WhisperModel(model_size, device="cuda", compute_type="float16")

    print("Transcribiendo...")
    segments_gen, info = model.transcribe(audio_path, language=None)

    segments = []
    full_text_parts = []

    for seg in segments_gen:
        segment_data = {
            "id": seg.id,
            "start": round(seg.start, 2),
            "end": round(seg.end, 2),
            "text": seg.text.strip(),
        }
        segments.append(segment_data)
        full_text_parts.append(seg.text.strip())

        # Progreso en tiempo real
        print(f"  [{seg.start:.1f}s - {seg.end:.1f}s] {seg.text.strip()}")

    elapsed = round(time.time() - start_time, 1)

    result = {
        "language": info.language,
        "language_probability": round(info.language_probability, 2),
        "duration_seconds": round(info.duration, 1),
        "processing_time_seconds": elapsed,
        "full_text": " ".join(full_text_parts),
        "segments": segments,
    }

    # Guardar JSON
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nTranscripción completada en {elapsed}s")
    print(f"Idioma detectado: {info.language} ({info.language_probability:.0%})")
    print(f"Segmentos: {len(segments)}")
    print(f"Guardado en: {output_path}")

    return result