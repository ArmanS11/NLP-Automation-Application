import json
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[2]
UPLOAD_DIR = ROOT / "uploads"
OUTPUT_DIR = ROOT / "outputs"
JOBS_DIR = ROOT / "jobs"
for d in (UPLOAD_DIR, OUTPUT_DIR, JOBS_DIR):
    d.mkdir(parents=True, exist_ok=True)

router = APIRouter()


class ProcessRequest(BaseModel):
    job_id: str
    mode: Optional[str] = "chunk"


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    job_id = uuid.uuid4().hex
    dest = UPLOAD_DIR / f"{job_id}_{file.filename}"
    with dest.open("wb") as f:
        f.write(await file.read())

    job = {
        "job_id": job_id,
        "filename": file.filename,
        "path": str(dest),
        "status": "uploaded",
    }
    (JOBS_DIR / f"{job_id}.json").write_text(json.dumps(job), encoding="utf-8")
    return {"job_id": job_id}


@router.post("/process")
def process(req: ProcessRequest):
    job_file = JOBS_DIR / f"{req.job_id}.json"
    if not job_file.exists():
        raise HTTPException(status_code=404, detail="job_id not found")

    if req.mode != "chunk":
        raise HTTPException(status_code=400, detail="only mode 'chunk' is supported in this POC")

    job = json.loads(job_file.read_text(encoding="utf-8"))
    if job.get("status") == "completed":
        return {"job_id": req.job_id, "status": "already_completed", "output": job.get("output")}

    try:
        from ingest_api.tasks import process_job

        process_job.apply_async(args=[req.job_id])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to enqueue job: {e}")

    job.update({"status": "processing"})
    job_file.write_text(json.dumps(job), encoding="utf-8")
    return {"job_id": req.job_id, "status": "queued"}


@router.get("/status/{job_id}")
def status(job_id: str):
    job_file = JOBS_DIR / f"{job_id}.json"
    if not job_file.exists():
        raise HTTPException(status_code=404, detail="job_id not found")
    return json.loads(job_file.read_text(encoding="utf-8"))


@router.get("/output/{job_id}")
def get_output(job_id: str):
    job_file = JOBS_DIR / f"{job_id}.json"
    if not job_file.exists():
        raise HTTPException(status_code=404, detail="job_id not found")

    job = json.loads(job_file.read_text(encoding="utf-8"))
    if job.get("status") != "completed":
        return {"status": job.get("status"), "message": "output not ready"}
    return {"output": job.get("output"), "chunks": job.get("chunks")}
