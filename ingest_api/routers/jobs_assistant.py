from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ingest_api.resume_tailor import tailor_resume
from ingest_api.sheets_logger import append_application_row

router = APIRouter()


class BulletSuggestionRequest(BaseModel):
    resume_text: str = Field(..., min_length=20)
    proficiencies: List[str] = Field(default_factory=list)
    job_title: str = Field(..., min_length=2)
    company: str = Field(..., min_length=2)
    job_description: str = Field(..., min_length=20)
    max_bullets: int = Field(default=8, ge=3, le=15)


class LogApplicationRequest(BaseModel):
    spreadsheet_id: str = Field(..., min_length=20)
    sheet_name: str = Field(default="Applications")
    url: str
    company: str
    job_title: str
    status: str = Field(default="Applied")
    suggested_bullets: List[str] = Field(default_factory=list)


@router.post("/suggest-bullets")
def suggest_bullets(req: BulletSuggestionRequest):
    tailored = tailor_resume(
        resume_text=req.resume_text,
        proficiencies=req.proficiencies,
        job_title=req.job_title,
        company=req.company,
        job_description=req.job_description,
        max_bullets=req.max_bullets,
    )
    return {"status": "ok", "tailored_resume": tailored}


@router.post("/log-application")
def log_application(req: LogApplicationRequest):
    try:
        result = append_application_row(
            spreadsheet_id=req.spreadsheet_id,
            sheet_name=req.sheet_name,
            url=req.url,
            company=req.company,
            title=req.job_title,
            status=req.status,
            suggested_bullets=req.suggested_bullets,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"sheet logging failed: {e}")

    return {"status": "ok", "sheets_response": result}
