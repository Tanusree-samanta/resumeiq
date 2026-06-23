"""POST /api/analyze endpoint."""

from fastapi import APIRouter, HTTPException
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.analyzer import analyze_resume

router = APIRouter(tags=["analyze"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analyze a resume against a job description.

    Supply either `resume_text` (plain text) or `resume_pdf` (base64-encoded PDF).
    """
    try:
        req.validate_resume_provided()
        return analyze_resume(req)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
