"""Extrae audio de un vídeo usando FFmpeg."""

import subprocess
from pathlib import Path


def extract_audio(video_path: str, output_path: str) -> str:
    """
    Extrae el audio de un vídeo a WAV mono 16kHz.
    
    Args:
        video_path: Ruta al fichero de vídeo.
        output_path: Ruta donde guardar el audio WAV.
    
    Returns:
        Ruta al fichero de audio generado.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", video_path,
            "-ar", "16000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            output_path,
        ],
        check=True,
        capture_output=True,
    )
    print(f"Audio extraído: {output_path}")
    return output_path