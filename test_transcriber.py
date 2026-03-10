"""Script de prueba para el transcriptor."""

import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from src.transcriber import extract_audio, transcribe


def main():
    video = "input/video.mp4"
    audio = "workspace/audio/video.wav"
    output = "workspace/transcriptions/video.json"

    # Paso 1: Extraer audio
    print("=" * 50)
    print("PASO 1: Extrayendo audio...")
    print("=" * 50)
    extract_audio(video, audio)

    # Paso 2: Transcribir
    print("\n" + "=" * 50)
    print("PASO 2: Transcribiendo...")
    print("=" * 50)
    result = transcribe(audio, output)

    # Resumen
    print("\n" + "=" * 50)
    print("RESUMEN")
    print("=" * 50)
    print(f"Idioma: {result['language']}")
    print(f"Duración vídeo: {result['duration_seconds']}s")
    print(f"Tiempo de proceso: {result['processing_time_seconds']}s")
    print(f"Segmentos: {len(result['segments'])}")
    print(f"JSON guardado en: {output}")


if __name__ == "__main__":
    main()