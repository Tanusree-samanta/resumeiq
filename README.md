# ResumeIQ – AI Resume Analyzer & Job Matcher 

> Upload your resume · paste a job description · get a match score, skill gap analysis, and actionable suggestions — powered by Claude AI.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![Anthropic](https://img.shields.io/badge/Claude-Sonnet_4.6-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

---




## Features

- **Match Score (0–100)** – overall resume-to-JD alignment
- **ATS Compatibility Score** – how well resume passes keyword filters
- **Keyword Density** – % of JD keywords found in resume
- **Skill Breakdown** – matched / partial / missing skills
- **Seniority Fit** – under / match / over-qualified detection
- **Actionable Suggestions** – prioritised (high / medium / low)
- **PDF Upload** – resume sent directly to Claude's vision API

---


## Project Structure

```
resumeiq/
├── frontend/
│   ├── index.html        # Single-page UI
│   ├── style.css         # Dark-mode design system
│   └── app.js            # API calls + result rendering
│
├── backend/
│   ├── main.py           # FastAPI app + static file serving
│   └── app/
│       ├── routers/
│       │   └── analyze.py        # POST /api/analyze
│       ├── services/
│       │   └── analyzer.py       # Claude API + NLP logic
│       ├── models/
│       │   └── schemas.py        # Pydantic request/response models
│       └── tests/
│           └── test_analyze.py   # Pytest unit tests
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/resumeiq.git
cd resumeiq
pip install -r requirements.txt
```

### 2. Set your API key

```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

### 3. Run the backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 4. Open in browser

Navigate to `http://localhost:8000` — the backend serves the frontend automatically.

---

## Running with Docker

```bash
cp .env.example .env   # add your API key
docker-compose up --build
# → http://localhost:8000
```

---

## Running Tests

```bash
cd backend 
pytest tests/ -v
```

---

## API Reference

### `POST /api/analyze`

**Request body:**

```json
{
  "job_description": "Full job description text (min 50 chars)...",
  "resume_text": "Plain text resume (optional if resume_pdf is given)",
  "resume_pdf": "Base64-encoded PDF bytes (optional if resume_text is given)"
}
```

**Response:**

```json
{
  "score": 78,
  "tier": "Strong",
  "summary": "Two-sentence analysis summary.",
  "matched_skills": ["Python", "PyTorch"],
  "missing_skills": ["Kubernetes"],
  "partial_skills": ["CI/CD"],
  "experience_years": 3,
  "seniority_fit": "Match",
  "suggestions": [
    { "priority": "high", "text": "Add Kubernetes to your projects." }
  ],
  "keyword_density": 65,
  "ats_score": 72
}
```

| Field | Type | Description |
|---|---|---|
| `score` | int 0–100 | Overall match score |
| `tier` | string | Excellent / Strong / Good / Fair / Weak |
| `ats_score` | int 0–100 | ATS keyword-filter compatibility |
| `keyword_density` | int 0–100 | % of JD keywords found in resume |
| `seniority_fit` | string | Under / Match / Over |

---

## AWS Deployment

### Option A – EC2 (simplest)

```bash
# On EC2 (Ubuntu 22.04, t3.small+)
sudo apt update && sudo apt install -y docker.io docker-compose
git clone https://github.com/YOUR_USERNAME/resumeiq.git
cd resumeiq
cp .env.example .env && nano .env   # add API key
docker-compose up -d
# Configure security group: open port 80 → 8000
```

### Option B – Elastic Beanstalk

1. Install EB CLI: `pip install awsebcli`
2. `eb init resumeiq --platform docker`
3. Set env var: `eb setenv ANTHROPIC_API_KEY=sk-ant-xxx`
4. `eb create resumeiq-prod && eb deploy`

### Option C – App Runner (recommended for prod)

1. Push Docker image to ECR
2. Create App Runner service from ECR image
3. Set `ANTHROPIC_API_KEY` in environment variables
4. App Runner handles auto-scaling, HTTPS, and zero downtime

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ Yes | – | Your Anthropic API key |
| `APP_ENV` | No | `development` | `development` or `production` |
| `ALLOWED_ORIGINS` | No | `*` | Comma-separated CORS origins |

---

## Tech Stack

| Layer | Technology |
|---|---|
| NLP / AI | Claude Sonnet 4.6 (Anthropic) |
| Backend | Python 3.12, FastAPI, Uvicorn |
| Data validation | Pydantic v2 |
| Frontend | Vanilla HTML / CSS / JS |
| Containerisation | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Deployment | AWS (EC2 / Beanstalk / App Runner) |

---

## License

MIT — see [LICENSE](LICENSE) for details.
