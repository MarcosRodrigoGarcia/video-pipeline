"""Script standalone para transcripción. Se ejecuta como subproceso para liberar GPU al terminar."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from src.transcriber import extract_audio, transcribe

if __name__ == "__main__":
    video_path = sys.argv[1]
    audio_path = sys.argv[2]
    trans_path = sys.argv[3]

    print("[1/5] Extrayendo audio...")
    extract_audio(video_path, audio_path)

    print("\n[2/5] Transcribiendo...")
    transcribe(audio_path, trans_path)
