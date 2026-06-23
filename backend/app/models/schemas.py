"""Pydantic schemas for request / response validation."""

from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


class AnalyzeRequest(BaseModel):
    job_description: str = Field(..., min_length=50)
    resume_text: Optional[str] = None
    resume_pdf: Optional[str] = None

    @field_validator("job_description")
    @classmethod
    def jd_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("job_description must not be blank")
        return v.strip()

    def validate_resume_provided(self) -> None:
        if not self.resume_text and not self.resume_pdf:
            raise ValueError("Provide either resume_text or resume_pdf")


class Suggestion(BaseModel):
    priority: Literal["high", "medium", "low"]
    text: str


class AnalyzeResponse(BaseModel):
    score: int = Field(..., ge=0, le=100)
    tier: Literal["Excellent", "Strong", "Good", "Fair", "Weak"]
    summary: str
    matched_skills: List[str]
    missing_skills: List[str]
    partial_skills: List[str]
    experience_years: Optional[int]
    seniority_fit: Literal["Under", "Match", "Over"]
    suggestions: List[Suggestion]
    keyword_density: int = Field(..., ge=0, le=100)
    ats_score: int = Field(..., ge=0, le=100)
