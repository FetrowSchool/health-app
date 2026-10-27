from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings, load_settings
from .database import initialize_database
from .routes.health import router
from .routes.activity import router as activity_router
from .routes.conversations import router as conversation_router
from .providers import build_provider, FeedbackProvider
from .voice_provider import VoiceProvider
from .routes.voice import router as voice_router


def create_app(settings: Settings | None = None, provider: FeedbackProvider | None = None, *, voice_transport=None) -> FastAPI:
    configuration = settings if settings is not None else load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        initialize_database(configuration.database_path)
        yield

    app = FastAPI(title="Pause coursework prototype", lifespan=lifespan)
    app.state.settings = configuration
    app.state.voice_provider = VoiceProvider(configuration, voice_transport)
    app.state.feedback_provider = provider if provider is not None else build_provider(configuration)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(configuration.cors_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "PUT"],
        allow_headers=["Accept", "Content-Type", "X-App-ID"],
    )
    app.include_router(router)
    app.include_router(activity_router)
    app.include_router(conversation_router)
    app.include_router(voice_router)
    return app


app = create_app()
