"""Unit tests for the analyze endpoint."""

import json
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

MOCK_RESPONSE = {
    "score": 78, "tier": "Strong",
    "summary": "Strong candidate with solid Python and ML background. Missing MLOps tooling experience.",
    "matched_skills": ["Python", "PyTorch", "FastAPI"],
    "missing_skills": ["Kubernetes", "MLflow"],
    "partial_skills": ["CI/CD"],
    "experience_years": 3, "seniority_fit": "Match",
    "suggestions": [
        {"priority": "high", "text": "Add Kubernetes experience to your resume."},
        {"priority": "medium", "text": "Include MLflow experiments in portfolio projects."},
    ],
    "keyword_density": 65, "ats_score": 72,
}

def _make_mock_message(data):
    block = MagicMock(); block.text = json.dumps(data)
    msg = MagicMock(); msg.content = [block]; return msg

@patch("app.services.analyzer.anthropic.Anthropic")
def test_analyze_text_resume(mock_cls):
    mock_client = MagicMock(); mock_cls.return_value = mock_client
    mock_client.messages.create.return_value = _make_mock_message(MOCK_RESPONSE)
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
        res = client.post("/api/analyze", json={
            "job_description": "Senior ML Engineer with Python, PyTorch, FastAPI, Kubernetes, and MLflow for production ML systems.",
            "resume_text": "ML Engineer with 3 years in Python, PyTorch, FastAPI. Built NLP pipelines.",
        })
    assert res.status_code == 200
    data = res.json()
    assert data["score"] == 78
    assert "Python" in data["matched_skills"]

@patch("app.services.analyzer.anthropic.Anthropic")
def test_analyze_pdf_resume(mock_cls):
    mock_client = MagicMock(); mock_cls.return_value = mock_client
    mock_client.messages.create.return_value = _make_mock_message(MOCK_RESPONSE)
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
        res = client.post("/api/analyze", json={
            "job_description": "Senior ML Engineer with Python, PyTorch, FastAPI, Kubernetes, and MLflow for production ML systems.",
            "resume_pdf": "JVBERi0xLjQKdGVzdA==",
        })
    assert res.status_code == 200

def test_missing_resume_returns_error():
    res = client.post("/api/analyze", json={
        "job_description": "Senior ML Engineer with Python cloud AWS Azure environments required.",
    })
    assert res.status_code in (422, 500)

def test_short_jd_returns_422():
    res = client.post("/api/analyze", json={"job_description": "short", "resume_text": "resume"})
    assert res.status_code == 422

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
