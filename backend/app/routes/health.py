from fastapi import APIRouter, Request

from ..health_controller import get_health
from ..models import HealthResponse

router = APIRouter(prefix="/api")


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    return get_health(request.app.state.settings)
