# Video Pipeline

Pipeline automatizado que convierte un vídeo en un documento DOCX estructurado, o en una transcripción en Markdown.

## Cómo funciona

**Modo completo (pipeline)**
```
Video (.mp4)
  │
  ├─ [1] Extracción de audio   → workspace/audio/*.wav              (FFmpeg, mono 16kHz)
  ├─ [2] Transcripción         → workspace/transcriptions/*.json    (faster-whisper, CUDA)
  ├─ [3] Resumen con LLM       → workspace/documents/*.md           (Ollama, llama3.1:8b)
  ├─ [4] Captura de frames     → workspace/frames/*.jpg             (FFmpeg, por sección)
  └─ [5] Generación de DOCX    → output/*.docx                      (python-docx)
```

**Modo solo transcripción**
```
Video (.mp4)
  │
  ├─ [1] Extracción de audio   → workspace/audio/*.wav
  ├─ [2] Transcripción         → workspace/transcriptions/*.json
  └─     Conversión a Markdown → output/*_transcripcion.md
```

## Requisitos

- Python 3.10+
- **FFmpeg** — debe estar en el PATH
- **CUDA GPU** — la transcripción usa `device="cuda"` con `compute_type="float16"`
- **Ollama** — debe estar corriendo localmente (`ollama serve`), modelo por defecto `llama3.1:8b`

## Instalación

```bash
pip install -r requirements.txt
```

Descargar el modelo de Ollama si no está disponible:

```bash
ollama pull llama3.1:8b
```

## Uso por línea de comandos

```bash
# Pipeline completo — usa input/video.mp4 por defecto
python pipeline.py

# Vídeo y tipo de documento personalizados
python pipeline.py input/mi_video.mp4 meeting_notes
python pipeline.py input/mi_video.mp4 summary
python pipeline.py input/mi_video.mp4 tutorial
```

El resultado se guarda en `output/<nombre_video>.docx`.

## Interfaz web

El proyecto incluye una interfaz web servida por FastAPI.

```bash
cd src/api
uvicorn server:app --host 0.0.0.0 --port 8000
```

Abre `frontend/index.html` en el navegador (o sírvelo con cualquier servidor estático).

**Opciones disponibles en la UI:**
- Subida de vídeo por arrastrar y soltar o selector de archivo
- Selector de tipo de documento (`meeting_notes`, `summary`, `tutorial`)
- Campo de contexto opcional (tema, asistentes, proyecto...)
- **Checkbox "Solo transcripción"** — omite el LLM y devuelve directamente un `.md` con la transcripción y timestamps `[MM:SS]`

## Tipos de documento

| Tipo | Descripción |
|------|-------------|
| `meeting_notes` | Actas de reunión con puntos clave y acciones (por defecto) |
| `summary` | Resumen conciso del contenido |
| `tutorial` | Formato de tutorial paso a paso |

Definidos en `src/summarizer/prompts.py`. Para añadir un tipo nuevo basta con añadir una entrada a `PROMPT_TEMPLATES`.

## Ejecución de etapas individuales

```bash
python test_transcriber.py   # Pasos 1-2: extracción de audio + transcripción
python test_summarizer.py    # Paso 3: resumen con LLM (requiere workspace/transcriptions/video.json)
python test_composer.py      # Pasos 4-5: captura de frames + generación de DOCX (requiere workspace/documents/)
```

## Estructura del proyecto

```
pipeline.py              # Orquesta los 5 pasos completos
transcribe_only.py       # Subproceso standalone: extracción + transcripción
src/
  api/
    server.py            # API FastAPI: /process, /status, /download
  transcriber/
    audio_extractor.py   # Wrapper FFmpeg → WAV
    whisper_transcriber.py # faster-whisper → JSON con segmentos y timestamps
  summarizer/
    llm_client.py        # Cliente HTTP para la API de Ollama (localhost:11434)
    prompts.py           # Plantillas de prompt: MEETING_NOTES, SUMMARY, TUTORIAL
    structurer.py        # Lee el JSON de transcripción, llama al LLM, extrae secciones
  composer/
    frame_extractor.py   # Wrapper FFmpeg → frames JPEG por sección
    image_placer.py      # Carga imágenes manuales desde image_manifest.json
    doc_builder.py       # Convierte Markdown + frames → DOCX via python-docx
frontend/
  index.html             # Interfaz web (vanilla JS)
input/                   # Vídeos de entrada
workspace/
  audio/                 # Ficheros WAV extraídos
  transcriptions/        # JSON de salida de Whisper
  documents/             # Markdown intermedio + JSON de secciones
  frames/                # Frames JPEG capturados (sec_00.jpg, sec_01.jpg, ...)
output/                  # DOCX finales y transcripciones .md
manual_images/           # Opcional: image_manifest.json + imágenes a inyectar
```

## Inyección manual de imágenes

Puedes sustituir los frames capturados automáticamente para secciones concretas aportando tus propias imágenes.

Crea `manual_images/image_manifest.json`:

```json
{
  "images": [
    { "section_id": "sec_01", "file": "manual_images/diagrama.png" },
    { "section_id": "sec_03", "file": "manual_images/grafico.png" }
  ]
}
```

Las imágenes manuales tienen prioridad sobre los frames automáticos para el mismo `section_id`.
