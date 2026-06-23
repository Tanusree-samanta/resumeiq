"""
ResumeIQ – FastAPI Backend
Run locally:  uvicorn main:app --reload --port 8000
"""
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
try:
    from fastapi.staticfiles import StaticFiles
except ImportError:
    from starlette.staticfiles import StaticFiles
try:
    from fastapi.responses import FileResponse
except ImportError:
    from starlette.responses import FileResponse
import os

from app.routers import analyze

app = FastAPI(
    title="ResumeIQ API",
    description="AI-powered resume analyzer and job matcher",
    version="1.0.0",
)

# ── CORS (tighten in production) ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # replace with your domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(analyze.router, prefix="/api")

# ── Serve frontend (optional – works when frontend/ is built next to main.py) ─
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(os.path.join(frontend_dir, "index.html"))

# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
