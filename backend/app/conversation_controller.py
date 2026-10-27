import asyncio
from starlette.concurrency import run_in_threadpool

from . import conversation_store as store
from .feedback_policy import FeedbackContext, accepted_response
from .providers import ProviderFailure


async def respond(settings, provider, app_id, payload):
    record, reserved = await run_in_threadpool(store.reserve, settings.database_path, app_id, payload, provider.mode)
    if not reserved:
        return record
    snapshot = record["context_used"]
    context = FeedbackContext(payload.exercise_type, payload.feedback, payload.user_message, snapshot.get("mood"), tuple(snapshot.get("recent", [])))
    failure = None
    text = None
    try:
        text = await asyncio.wait_for(provider.generate(context), timeout=settings.provider_timeout_seconds)
        if not accepted_response(text, payload.feedback, payload.exercise_type):
            failure = 'invalid_response'
    except (TimeoutError, asyncio.TimeoutError):
        failure = 'provider_timeout'
    except ProviderFailure as error:
        failure = error.code if error.code in {'provider_timeout','provider_error','invalid_response','missing_configuration'} else 'provider_error'
    except Exception:
        # No raw exception text, rejected output, credentials or headers in logs,
        # responses or failure records. Exercise/session state is never changed.
        failure = 'provider_error'
    return await run_in_threadpool(store.finalize, settings.database_path, app_id, record['id'], text if failure is None else None, failure)

