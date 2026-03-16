import sys, uuid, shutil, threading
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from pipeline import run

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# job_id -> { "status": "pending|running|done|error", "output": path, "error": msg }
jobs = {}


def run_pipeline(job_id: str, input_path: str, doc_type: str, output_name: str):
    jobs[job_id]["status"] = "running"
    try:
        run(input_path, doc_type=doc_type, output_name=output_name)
        jobs[job_id]["status"] = "done"
        jobs[job_id]["output"] = f"output/{output_name}.docx"
    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)
    finally:
        Path(input_path).unlink(missing_ok=True)


@app.post("/process")
async def process_video(
    video: UploadFile = File(...),
    doc_type: str = Form("meeting_notes"),
):
    if doc_type not in ("meeting_notes", "summary", "tutorial"):
        raise HTTPException(status_code=400, detail="doc_type inválido")

    job_id = uuid.uuid4().hex[:8]
    input_path = f"input/upload_{job_id}.mp4"
    output_name = f"output_{job_id}"

    Path("input").mkdir(exist_ok=True)
    with open(input_path, "wb") as f:
        shutil.copyfileobj(video.file, f)

    jobs[job_id] = {"status": "pending", "output": None, "error": None}

    thread = threading.Thread(target=run_pipeline, args=(job_id, input_path, doc_type, output_name), daemon=True)
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
    return FileResponse(
        job["output"],
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="documento.docx",
    )
