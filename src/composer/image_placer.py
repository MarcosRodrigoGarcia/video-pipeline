import json
from pathlib import Path

def load_manual_images(manifest_path):
    if not Path(manifest_path).exists():
        return {}
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    images = {}
    for img in manifest.get("images", []):
        section_id = img.get("section_id")
        file_path = img.get("file")
        if section_id and file_path and Path(file_path).exists():
            images[section_id] = file_path
            print(f"  Imagen manual: {section_id} -> {file_path}")
        elif file_path and not Path(file_path).exists():
            print(f"  AVISO: Imagen no encontrada: {file_path}")
    return images
