"""
Core NLP analysis service.

Sends resume + JD to Claude and parses structured JSON response.
Claude acts as both the NLP extraction layer (TF-IDF / BERT equivalent)
and the scoring/recommendation engine.
"""

from __future__ import annotations
import json, os
from groq import Groq
from app.models.schemas import AnalyzeRequest, AnalyzeResponse, Suggestion

SYSTEM_PROMPT = """You are an expert technical recruiter and NLP-based resume analyzer.

Given a resume and a job description, analyse them deeply and return ONLY a valid JSON
object — no markdown fences, no preamble, no trailing text.

Required JSON structure:
{
  "score": <integer 0-100, overall match>,
  "tier": <"Excellent"|"Strong"|"Good"|"Fair"|"Weak">,
  "summary": <string, exactly 2 sentences>,
  "matched_skills":  [<string>, ...],
  "missing_skills":  [<string>, ...],
  "partial_skills":  [<string>, ...],
  "experience_years": <integer or null>,
  "seniority_fit": <"Under"|"Match"|"Over">,
  "suggestions": [
    {"priority": <"high"|"medium"|"low">, "text": <string>},
    ...
  ],
  "keyword_density": <integer 0-100>,
  "ats_score":       <integer 0-100>
}

Scoring rubric:
- 85-100 Excellent, 70-84 Strong, 55-69 Good, 40-54 Fair, <40 Weak
- ATS score: how well the resume passes keyword-based filters
- Keyword density: % of JD keywords present in resume
- Provide 4-6 specific, actionable suggestions ordered by impact
"""


def _build_gemini_prompt(req: AnalyzeRequest) -> str:
    resume = req.resume_text or "[No resume text — PDF not supported in this mode]"
    return f"Resume:\n{resume}\n\nJob Description:\n{req.job_description}\n\nReturn the JSON analysis."


def analyze_resume(req: AnalyzeRequest) -> AnalyzeResponse:
    req.validate_resume_provided()
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY environment variable not set")

    client = Groq(api_key=api_key)
    try:
        message = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_gemini_prompt(req)},
            ],
            temperature=0.2,
        )
    except Exception as exc:
        raise RuntimeError(f"Groq API error: {exc}") from exc

    raw = message.choices[0].message.content
    clean = raw.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
    clean = clean.strip().rstrip("`").strip()

    try:
        data = json.loads(clean)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse AI response: {exc}\nRaw: {raw[:300]}") from exc

    suggestions = [Suggestion(priority=s.get("priority", "medium"), text=s.get("text", "")) for s in data.get("suggestions", [])]

    return AnalyzeResponse(
        score=int(data.get("score", 0)),
        tier=data.get("tier", "Fair"),
        summary=data.get("summary", ""),
        matched_skills=data.get("matched_skills", []),
        missing_skills=data.get("missing_skills", []),
        partial_skills=data.get("partial_skills", []),
        experience_years=data.get("experience_years"),
        seniority_fit=data.get("seniority_fit", "Match"),
        suggestions=suggestions,
        keyword_density=int(data.get("keyword_density", 0)),
        ats_score=int(data.get("ats_score", 0)),
    )