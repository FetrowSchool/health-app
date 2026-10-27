"""Voice bootstrap only; does not mutate exercise, conversation or mood records."""
from fastapi import HTTPException
from .voice_models import VoiceConfigResponse
from .voice_provider import VoiceFailure


def voice_error(status, message):
    return HTTPException(status, message, headers={'Cache-Control': 'no-store'})


def configuration(settings):
    return VoiceConfigResponse(status='configured' if settings.voice_configured else 'unconfigured',
                               duration_seconds=settings.voice_duration_seconds)


async def create_session(provider, offer):
    try:
        return await provider.create(offer)
    except VoiceFailure as error:
        status, message = {
            'unconfigured': (503, 'Voice is not configured.'),
            'timeout': (504, 'Voice session creation timed out.'),
        }.get(error.code, (502, 'Voice session could not be created.'))
        raise voice_error(status, message) from None


async def close_session(provider, session_id):
    try:
        await provider.close(session_id)
        # An accepted hangup request is not a session.closed/final-billing receipt.
        return {'status': 'close_requested'}
    except VoiceFailure as error:
        status = {'unknown_session': 404, 'timeout': 504}.get(error.code, 502)
        raise voice_error(status, 'Voice closure could not be confirmed.') from None
