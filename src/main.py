from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .openclaw_api import get_config, get_metrics, get_recent_activity, get_sessions, get_skills, get_status

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
async def dashboard_data() -> dict[str, Any]:
    status_data = get_status()
    sessions = get_sessions()
    skills = get_skills()
    config = get_config()
    recent_activity = get_recent_activity()
    metrics = get_metrics()

    active_sessions = sum(1 for session in sessions if session.get("status") == "active")
    loaded_skills = sum(1 for skill in skills if skill.get("loaded") is True)

    token_used = int(config.get("token_used", 0) or 0)
    token_limit = int(config.get("token_limit", 0) or 0)
    token_percent = round((token_used / token_limit) * 100, 1) if token_limit else 0.0

    return {
        "status": str(status_data.get("status", "offline")),
        "current_task": str(status_data.get("current_task") or "暂无任务"),
        "runtime_seconds": int(status_data.get("runtime_seconds", 0) or 0),
        "version": str(config.get("version") or "v0.0.0"),
        "model": str(config.get("model") or "unknown"),
        "token_usage": {
            "used": token_used,
            "limit": token_limit,
            "percent": token_percent,
        },
        "summary": {
            "total_sessions": len(sessions),
            "active_sessions": active_sessions,
            "total_skills": len(skills),
            "loaded_skills": loaded_skills,
        },
        "sessions": sessions,
        "skills": skills,
        "recent_activity": recent_activity,
        "metrics": metrics,
    }
