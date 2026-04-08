import sys, uuid, shutil, threading, subprocess, traceback, json
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

PYTHON = sys.executable
ROOT = str(Path(__file__).parent.parent.parent)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# job_id -> { "status": "pending|running|done|error", "output": path, "error": msg, "mode": "full|transcribe" }
jobs = {}


def _seconds_to_mmss(seconds: float) -> str:
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m:02d}:{s:02d}"


def _json_to_md(trans_path: str, md_path: str):
    with open(trans_path, encoding="utf-8") as f:
        data = json.load(f)
    lines = [f"# Transcripción\n"]
    for seg in data.get("segments", []):
        ts = _seconds_to_mmss(seg["start"])
        lines.append(f"**[{ts}]** {seg['text']}\n")
    Path(md_path).parent.mkdir(parents=True, exist_ok=True)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def run_pipeline(job_id: str, input_path: str, doc_type: str, output_name: str, context: str = ""):
    jobs[job_id]["status"] = "running"
    try:
        cmd = [PYTHON, "pipeline.py", input_path, doc_type, output_name, context]
        result = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=False,
            timeout=1800,
        )
        if result.returncode == 0:
            jobs[job_id]["status"] = "done"
            jobs[job_id]["output"] = f"output/{output_name}.docx"
        else:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = f"El pipeline terminó con código {result.returncode}"
    except subprocess.TimeoutExpired:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = "Timeout: el pipeline tardó más de 30 minutos"
    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)
        print(f"\n[ERROR job {job_id}]\n{traceback.format_exc()}")
    finally:
        Path(input_path).unlink(missing_ok=True)


def run_transcribe_only(job_id: str, input_path: str, output_name: str):
    jobs[job_id]["status"] = "running"
    try:
        audio_path = f"workspace/audio/{output_name}.wav"
        trans_path = f"workspace/transcriptions/{output_name}.json"
        md_path = f"output/{output_name}_transcripcion.md"

        result = subprocess.run(
            [PYTHON, "transcribe_only.py", input_path, audio_path, trans_path],
            cwd=ROOT,
            capture_output=False,
            timeout=1800,
        )
        if result.returncode != 0 and not Path(trans_path).exists():
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = f"La transcripción terminó con código {result.returncode}"
            return

        Path("output").mkdir(exist_ok=True)
        _json_to_md(trans_path, md_path)
        jobs[job_id]["status"] = "done"
        jobs[job_id]["output"] = md_path
    except subprocess.TimeoutExpired:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = "Timeout: la transcripción tardó más de 30 minutos"
    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)
        print(f"\n[ERROR job {job_id}]\n{traceback.format_exc()}")
    finally:
        Path(input_path).unlink(missing_ok=True)


@app.post("/process")
async def process_video(
    video: UploadFile = File(...),
    doc_type: str = Form("meeting_notes"),
    context: str = Form(""),
    transcribe_only: str = Form("false"),
):
    only_transcribe = transcribe_only.lower() == "true"

    if not only_transcribe and doc_type not in ("meeting_notes", "summary", "tutorial"):
        raise HTTPException(status_code=400, detail="doc_type inválido")

    job_id = uuid.uuid4().hex[:8]
    video_stem = Path(video.filename).stem if video.filename else "video"
    date_str = datetime.now().strftime("%Y%m%d_%H%M")
    input_path = f"input/upload_{job_id}.mp4"
    output_name = f"{video_stem}_{date_str}"

    Path("input").mkdir(exist_ok=True)
    with open(input_path, "wb") as f:
        shutil.copyfileobj(video.file, f)

    jobs[job_id] = {"status": "pending", "output": None, "error": None, "mode": "transcribe" if only_transcribe else "full"}

    if only_transcribe:
        thread = threading.Thread(target=run_transcribe_only, args=(job_id, input_path, output_name), daemon=True)
    else:
        thread = threading.Thread(target=run_pipeline, args=(job_id, input_path, doc_type, output_name, context), daemon=True)
    thread.start()

    return JSONResponse({"job_id": job_id})


@app.get("/status/{job_id}")
def get_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    return JSONResponse({"status": job["status"], "error": job.get("error")})


@app.get("/download/{job_id}")
def download(job_id: str):
    job = jobs.get(job_id)
    if not job or job["status"] != "done":
        raise HTTPException(status_code=404, detail="Archivo no disponible")

    output = job["output"]
    if job.get("mode") == "transcribe":
        return FileResponse(
            output,
            media_type="text/markdown",
            filename=Path(output).name,
        )
    return FileResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"{Path(output).stem}.docx",
    )
