"""Isolated local Live bootstrap: no database, exercise provider, tools or RAG imports."""
from contextlib import asynccontextmanager
from dataclasses import replace
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import load_settings
from .routes.voice import router
from .voice_provider import VoiceProvider

INSTRUCTIONS = "Speak briefly and naturally. This is a fictional audio connection test. Do not delegate tasks or give advice."


def create_diagnostic_app(settings=None, *, transport=None):
    configuration = settings if settings is not None else load_settings()
    if configuration.voice_live_model != 'gpt-live-1':
        raise ValueError('Diagnostic VOICE_LIVE_MODEL must be gpt-live-1.')
    configuration = replace(configuration, voice_duration_seconds=30)
    session = {'model': configuration.voice_live_model, 'instructions': INSTRUCTIONS,
               'store': False, 'triggers': []}
    # Omitted delegation selects client handling, with no handler/tools/model here.
    # No Responses/Decisions calls or background record access are configured.
    provider = VoiceProvider(configuration, session_config=session, config_label='diagnostic')

    @asynccontextmanager
    async def lifespan(app):
        # Prepare lazy HTTP/TLS dependencies before the server advertises readiness.
        actual_transport = transport if transport is not None else httpx.AsyncHTTPTransport(retries=0)
        async with httpx.AsyncClient(transport=actual_transport, trust_env=False, follow_redirects=False,
                timeout=httpx.Timeout(configuration.voice_timeout_seconds,
                                      connect=min(3, configuration.voice_timeout_seconds))) as client:
            provider.client = client
            try:
                yield
            finally:
                provider.client = None

    app = FastAPI(title='Pause isolated voice diagnostic', lifespan=lifespan)
    app.state.settings = configuration
    app.state.voice_provider = provider
    app.add_middleware(CORSMiddleware, allow_origins=list(configuration.cors_origins),
                       allow_methods=['GET', 'POST'], allow_headers=['Content-Type'])
    app.include_router(router)
    return app


app = create_diagnostic_app()
