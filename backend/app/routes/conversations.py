from uuid import UUID
from fastapi import APIRouter, Request, Response

from .activity import AppID
from ..conversation_controller import respond
from ..conversation_store import retrieve
from ..models import FeedbackRequest, ConversationResponse

router = APIRouter(prefix='/api')


@router.post('/feedback-response', response_model=ConversationResponse)
async def feedback_response(request: Request, response: Response, app_id: AppID, payload: FeedbackRequest):
    result = await respond(request.app.state.settings, request.app.state.feedback_provider, app_id, payload)
    if result['status'] == 'pending':
        response.status_code = 202
    return result


@router.get('/conversations/{conversation_id}', response_model=ConversationResponse)
def conversation(request: Request, app_id: AppID, conversation_id: UUID):
    return retrieve(request.app.state.settings.database_path, app_id, conversation_id)

