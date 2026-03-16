import sys, uuid, shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from pipeline import run

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

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

    try:
        run(input_path, doc_type=doc_type, output_name=output_name)
    except Exception as e:
        Path(input_path).unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=str(e))

    Path(input_path).unlink(missing_ok=True)

    output_path = f"output/{output_name}.docx"
    return FileResponse(
        output_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="documento.docx",
    )
