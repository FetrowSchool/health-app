from fastapi import APIRouter, Request, Response
from pydantic import ValidationError
from ..voice_controller import configuration, create_session, close_session, voice_error
from ..voice_models import MAX_REQUEST_BYTES, MAX_SDP_BYTES, VoiceOffer, VoiceConfigResponse, VoiceSessionResponse, VoiceCloseRequest, VoiceCloseResponse
from ..voice_provider import strict_json

router = APIRouter(prefix='/api/voice')


@router.get('/config', response_model=VoiceConfigResponse)
def config(request: Request, response: Response):
    if request.query_params:
        raise voice_error(422, 'Invalid voice request.')
    response.headers['Cache-Control'] = 'no-store'
    return configuration(request.app.state.settings)


async def read_payload(request, limit=MAX_REQUEST_BYTES):
    if request.query_params:
        raise voice_error(422, 'Invalid voice request.')
    if request.headers.get('content-type', '').split(';')[0].strip().lower() != 'application/json':
        raise voice_error(415, 'Voice requests require JSON.')
    length = request.headers.get('content-length')
    if length is not None:
        try:
            length = int(length)
            if length < 0:
                raise ValueError
        except ValueError:
            raise voice_error(400, 'Invalid voice request.') from None
        if length > limit:
            raise voice_error(413, 'Voice request is too large.')
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > limit:
            raise voice_error(413, 'Voice request is too large.')
    try:
        payload = strict_json(body.decode('utf-8'))
    except (ValueError, UnicodeError, RecursionError):
        raise voice_error(400, 'Invalid voice request.') from None
    return payload


async def read_offer(request):
    payload = await read_payload(request)
    if isinstance(payload, dict) and isinstance(payload.get('sdp'), str):
        try:
            size = len(payload['sdp'].encode('utf-8'))
        except UnicodeError:
            raise voice_error(422, 'Invalid voice request.') from None
        if size > MAX_SDP_BYTES:
            raise voice_error(413, 'Voice request is too large.')
    try:
        return VoiceOffer.model_validate(payload)
    except (ValidationError, ValueError):
        # Default validation errors include rejected inputs; do not echo SDP/secrets.
        raise voice_error(422, 'Invalid voice request.') from None


@router.post('/sessions', response_model=VoiceSessionResponse, status_code=201,
             openapi_extra={'requestBody': {'required': True, 'content': {
                 'application/json': {'schema': VoiceOffer.model_json_schema()}}}})
async def sessions(request: Request, response: Response):
    offer = await read_offer(request)
    result = await create_session(request.app.state.voice_provider, offer)
    if await request.is_disconnected():
        await close_session(request.app.state.voice_provider, result.session_id)
        raise voice_error(499, 'Voice request ended.')
    response.headers['Cache-Control'] = 'no-store'
    return result


@router.post('/sessions/close', response_model=VoiceCloseResponse, openapi_extra={'requestBody': {'required': True, 'content': {
    'application/json': {'schema': VoiceCloseRequest.model_json_schema()}}}})
async def close(request: Request, response: Response):
    payload = await read_payload(request, 1024)
    try:
        command = VoiceCloseRequest.model_validate(payload)
    except (ValidationError, ValueError):
        raise voice_error(422, 'Invalid voice request.') from None
    result = await close_session(request.app.state.voice_provider, command.session_id)
    response.headers['Cache-Control'] = 'no-store'
    return result
