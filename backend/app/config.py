"""Backend-only configuration; no credentials are returned to the browser."""
from dataclasses import dataclass, field
import os
import math
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / "backend" / ".env"


@dataclass(frozen=True)
class Settings:
    database_path: Path = PROJECT_ROOT / "data" / "app.sqlite3"
    cors_origins: tuple[str, ...] = ("http://127.0.0.1:5173", "http://localhost:5173")
    model_api_key: str = field(default="", repr=False)

    model_provider: str = "mock"
    model_name: str = ""
    model_endpoint: str = ""
    provider_timeout_seconds: float = 4.0

    voice_api_key: str = field(default="", repr=False)
    voice_backend_model: str = ""
    voice_live_model: str = "gpt-live-1"
    voice_duration_seconds: int = 60
    voice_timeout_seconds: float = 10.0
    voice_diagnostics: bool = False

    def __post_init__(self):
        if (type(self.voice_duration_seconds) is not int or not 1 <= self.voice_duration_seconds <= 300
                or isinstance(self.voice_timeout_seconds, bool)
                or not math.isfinite(self.voice_timeout_seconds) or not 0.1 <= self.voice_timeout_seconds <= 25):
            raise ValueError('Invalid voice duration or timeout configuration.')

    @property
    def voice_configured(self) -> bool:
        key = self.voice_api_key.strip()
        return bool(key) and not any(ord(char) < 33 or ord(char) > 126 for char in key)

    @property
    def model_configured(self) -> bool:
        return bool(self.model_api_key.strip())


def load_settings() -> Settings:
    load_dotenv(ENV_FILE, override=False)
    origins = tuple(item.strip() for item in os.getenv(
        "CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173"
    ).split(",") if item.strip())
    try:
        timeout = float(os.getenv("MODEL_TIMEOUT_SECONDS", "4"))
        if not 1 <= timeout <= 25:
            raise ValueError
    except ValueError:
        raise ValueError("MODEL_TIMEOUT_SECONDS must be between 1 and 25 seconds.") from None
    try:
        voice_duration = int(os.getenv('VOICE_SESSION_DURATION_SECONDS', '60'))
        voice_timeout = float(os.getenv('VOICE_PROVIDER_TIMEOUT_SECONDS', '10'))
    except ValueError:
        raise ValueError('Invalid voice duration or timeout configuration.') from None
    return Settings(
        voice_api_key=os.getenv('OPENAI_API_KEY', '').strip(),
        voice_diagnostics=os.getenv('VOICE_DIAGNOSTICS', '') == '1',
        voice_backend_model=os.getenv('VOICE_BACKEND_MODEL', '').strip(),
        voice_live_model=os.getenv('VOICE_LIVE_MODEL', 'gpt-live-1').strip(),
        voice_duration_seconds=voice_duration, voice_timeout_seconds=voice_timeout,
        cors_origins=origins, model_api_key=os.getenv("MODEL_API_KEY", ""),
        model_provider=os.getenv("MODEL_PROVIDER", "mock").strip().lower(),
        provider_timeout_seconds=timeout,
        model_name=os.getenv("MODEL_NAME", "").strip(),
        model_endpoint=os.getenv("MODEL_ENDPOINT", "").strip(),
    )
