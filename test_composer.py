import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from src.composer import capture_section_frames, build_docx, load_manual_images

def main():
    video = "input/video.mp4"
    markdown = "workspace/documents/video.md"
    sections_file = "workspace/documents/sections.json"
    frames_dir = "workspace/frames"
    output = "output/video_documento.docx"
    manifest = "manual_images/image_manifest.json"
    with open(sections_file, "r", encoding="utf-8") as f:
        sections_data = json.load(f)
    sections = sections_data["sections"]
    print("=" * 50)
    print("PASO 1: Capturando frames del video...")
    print("=" * 50)
    frames = capture_section_frames(video, sections, frames_dir)
    print(f"Frames capturados: {len(frames)}")
    print("\n" + "=" * 50)
    print("PASO 2: Cargando imagenes manuales...")
    print("=" * 50)
    manual = load_manual_images(manifest)
    print(f"Imagenes manuales: {len(manual)}")
    print("\n" + "=" * 50)
    print("PASO 3: Generando documento DOCX...")
    print("=" * 50)
    build_docx(markdown, frames, output, manual)
    print("\n" + "=" * 50)
    print("COMPLETADO")
    print("=" * 50)
    print(f"Documento final: {output}")

if __name__ == "__main__":
    main()
