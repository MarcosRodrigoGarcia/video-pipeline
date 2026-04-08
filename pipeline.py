import sys, json, time, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from src.summarizer import summarize, load_model
from src.composer import capture_section_frames, build_docx, load_manual_images

PYTHON = sys.executable
ROOT   = str(Path(__file__).parent)

def run(video_path, doc_type="meeting_notes", output_name=None, context=""):
    start = time.time()
    name = Path(video_path).stem
    if output_name is None:
        output_name = name
    audio         = f"workspace/audio/{name}.wav"
    trans         = f"workspace/transcriptions/{name}.json"
    md            = f"workspace/documents/{name}.md"
    sections_file = f"workspace/documents/{name}_sections.json"
    frames_dir    = "workspace/frames"
    output        = f"output/{output_name}.docx"
    manifest      = "manual_images/image_manifest.json"

    print("=" * 50)
    print(f"PIPELINE: {video_path}")
    print(f"Tipo: {doc_type}")
    print("=" * 50)

    # Pasos 1-2 en subproceso propio para liberar GPU antes de llamar a Ollama
    subprocess.run(
        [PYTHON, "transcribe_only.py", video_path, audio, trans],
        cwd=ROOT,
    )
    # ctranslate2 crashea al limpiar CUDA al salir (código 3221226505 en Windows)
    # pero la transcripción sí se completa — verificamos que el JSON existe
    if not Path(trans).exists():
        raise RuntimeError("La transcripción falló: archivo JSON no generado")

    print("\nCargando modelo LLM...")
    load_model()

    print("\n[3/5] Generando resumen...")
    result = summarize(trans, md, sections_file, doc_type=doc_type, context=context)

    print("\n[4/5] Capturando frames...")
    frames = capture_section_frames(video_path, result["sections"], frames_dir)

    print("\n[5/5] Generando documento...")
    manual = load_manual_images(manifest)
    build_docx(md, frames, output, manual)

    elapsed = round(time.time() - start, 1)
    print("\n" + "=" * 50)
    print(f"COMPLETADO en {elapsed}s")
    print(f"Documento: {output}")
    print("=" * 50)

if __name__ == "__main__":
    video      = sys.argv[1] if len(sys.argv) > 1 else "input/video.mp4"
    doc_type   = sys.argv[2] if len(sys.argv) > 2 else "meeting_notes"
    output_name = sys.argv[3] if len(sys.argv) > 3 else None
    context = sys.argv[4] if len(sys.argv) > 4 else ""
    run(video, doc_type, output_name, context)
