import sqlite3
from fastapi import HTTPException

from .config import Settings
from .database import database_ready
from .models import HealthResponse


def get_health(settings: Settings) -> HealthResponse:
    try:
        ready = database_ready(settings.database_path)
    except sqlite3.Error:
        ready = False
    if not ready:
        raise HTTPException(status_code=503, detail="Local database is unavailable.")
    return HealthResponse(status="ok", database="ready", model_configured=settings.model_configured)
