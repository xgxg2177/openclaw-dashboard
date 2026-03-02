from pathlib import Path
from typing import Union

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .openclaw_api import get_sessions, get_skills, get_status

app = FastAPI(title="OpenClaw Dashboard")

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
STATIC_DIR = BASE_DIR / "static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request, "title": "OpenClaw Dashboard"})


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/dashboard")
async def dashboard_data() -> dict[str, Union[str, int]]:
    status_data = get_status()
    sessions = get_sessions()
    skills = get_skills()

    active_sessions = sum(1 for session in sessions if session.get("status") == "active")
    loaded_skills = sum(1 for skill in skills if skill.get("loaded") is True)

    return {
        "status": str(status_data.get("status", "offline")),
        "current_task": str(status_data.get("current_task") or "暂无任务"),
        "active_sessions": active_sessions,
        "loaded_skills": loaded_skills,
    }
