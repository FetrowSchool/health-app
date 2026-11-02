from typing import Annotated
from fastapi import APIRouter, Query, Request, Response
from .activity import AppID
from ..history_controller import read_history
from ..models import HistoryResponse

router = APIRouter(prefix='/api')


@router.get('/history', response_model=HistoryResponse)
def history(request: Request, response: Response, app_id: AppID,
            limit: Annotated[int, Query(ge=1, le=50)] = 20):
    response.headers['Cache-Control'] = 'no-store'
    return read_history(request.app.state.settings.database_path, app_id, limit)
