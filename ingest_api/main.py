from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from ingest_api.routers.admin import router as admin_router
from ingest_api.routers.ingest import router as ingest_router
from ingest_api.routers.jobs_assistant import router as jobs_assistant_router

app = FastAPI(title="NLP POC - Ingest + Job Application Assistant")

app.include_router(ingest_router, prefix="/ingest", tags=["ingest"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(jobs_assistant_router, prefix="/jobs", tags=["jobs"])

app.mount("/files", StaticFiles(directory="outputs"), name="files")


@app.get("/health")
def health():
    return {"status": "ok"}
