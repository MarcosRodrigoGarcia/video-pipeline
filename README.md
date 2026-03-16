# Video Pipeline

Automated pipeline that converts a video file into a structured DOCX document.

## How it works

```
Video (.mp4)
  │
  ├─ [1] Audio extraction    → workspace/audio/*.wav         (FFmpeg, mono 16kHz)
  ├─ [2] Transcription       → workspace/transcriptions/*.json (faster-whisper, CUDA)
  ├─ [3] LLM summarization   → workspace/documents/*.md       (Ollama, llama3.1:8b)
  ├─ [4] Frame capture       → workspace/frames/*.jpg         (FFmpeg, per section)
  └─ [5] DOCX generation     → output/*.docx                  (python-docx)
```

## Requirements

- Python 3.10+
- **FFmpeg** — must be in PATH
- **CUDA GPU** — transcription runs on `device="cuda"` with `compute_type="float16"`
- **Ollama** — must be running locally (`ollama serve`), default model `llama3.1:8b`

## Installation

```bash
pip install -r requirements.txt
```

Pull the Ollama model if you haven't already:

```bash
ollama pull llama3.1:8b
```

## Usage

```bash
# Full pipeline — uses input/video.mp4 by default
python pipeline.py

# Custom video file
python pipeline.py input/my_video.mp4

# Custom video + document type
python pipeline.py input/my_video.mp4 meeting_notes
python pipeline.py input/my_video.mp4 summary
python pipeline.py input/my_video.mp4 tutorial
```

Output is saved to `output/<video_name>.docx`.

## Document types

| Type | Description |
|------|-------------|
| `meeting_notes` | Structured meeting notes with action items (default) |
| `summary` | Concise summary of the content |
| `tutorial` | Step-by-step tutorial format |

Defined in `src/summarizer/prompts.py`. Add a new entry to `PROMPT_TEMPLATES` to create a custom type.

## Running individual stages

```bash
python test_transcriber.py   # Steps 1-2: audio extraction + transcription
python test_summarizer.py    # Step 3: LLM summarization (requires workspace/transcriptions/video.json)
python test_composer.py      # Steps 4-5: frame capture + DOCX build (requires workspace/documents/)
```

## Project structure

```
pipeline.py              # Orchestrates all 5 steps end-to-end
src/
  transcriber/
    audio_extractor.py   # FFmpeg wrapper → WAV
    whisper_transcriber.py # faster-whisper → JSON with segments + timestamps
  summarizer/
    llm_client.py        # HTTP client for Ollama API (localhost:11434)
    prompts.py           # Prompt templates: MEETING_NOTES, SUMMARY, TUTORIAL
    structurer.py        # Reads transcription JSON, calls LLM, extracts sections
  composer/
    frame_extractor.py   # FFmpeg wrapper → JPEG frames per section
    image_placer.py      # Loads manual images from image_manifest.json
    doc_builder.py       # Converts Markdown + frames → DOCX via python-docx
input/                   # Source video files
workspace/
  audio/                 # Extracted WAV files
  transcriptions/        # Whisper output JSON
  documents/             # Intermediate Markdown + sections JSON
  frames/                # Captured JPEG frames (sec_00.jpg, sec_01.jpg, ...)
output/                  # Final DOCX files
manual_images/           # Optional: image_manifest.json + images to inject
```

## Manual image injection

You can override auto-captured frames for specific sections by providing your own images.

Create `manual_images/image_manifest.json`:

```json
{
  "images": [
    { "section_id": "sec_01", "file": "manual_images/diagram.png" },
    { "section_id": "sec_03", "file": "manual_images/chart.png" }
  ]
}
```

Manual images take precedence over auto-captured frames for the same `section_id`.
