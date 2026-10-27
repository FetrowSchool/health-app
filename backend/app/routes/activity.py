from datetime import date
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Header, Request

from .. import activity_controller as controller
from ..models import SessionStart, SessionEnd, SessionResponse, FeedbackInput, MoodInput, MoodResponse

router = APIRouter(prefix='/api')
AppID = Annotated[UUID, Header(alias='X-App-ID')]


@router.post('/sessions', response_model=SessionResponse)
def start(request: Request, app_id: AppID, payload: SessionStart):
    return controller.start_session(request.app.state.settings.database_path, app_id, payload)


@router.get('/sessions/{session_id}', response_model=SessionResponse)
def read(request: Request, app_id: AppID, session_id: UUID):
    return controller.read_session(request.app.state.settings.database_path, app_id, session_id)


@router.patch('/sessions/{session_id}', response_model=SessionResponse)
def finish(request: Request, app_id: AppID, session_id: UUID, payload: SessionEnd):
    return controller.end_session(request.app.state.settings.database_path, app_id, session_id, payload)


@router.put('/sessions/{session_id}/feedback', response_model=SessionResponse)
def feedback(request: Request, app_id: AppID, session_id: UUID, payload: FeedbackInput):
    return controller.save_feedback(request.app.state.settings.database_path, app_id, session_id, payload.feedback)


@router.put('/mood-checkins/{local_date}', response_model=MoodResponse)
def mood(request: Request, app_id: AppID, local_date: date, payload: MoodInput):
    return controller.save_mood(request.app.state.settings.database_path, app_id, local_date, payload.mood)


@router.get('/mood-checkins/{local_date}', response_model=MoodResponse)
def get_mood(request: Request, app_id: AppID, local_date: date):
    return controller.read_mood(request.app.state.settings.database_path, app_id, local_date)
