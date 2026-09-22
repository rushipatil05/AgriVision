from fastapi import APIRouter
from app.config.settings import settings
from app.schemas.common import HealthResponse, ModelsStatusResponse
from app.services.model_manager import model_manager

router = APIRouter(tags=["System & Diagnostics"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Health Check",
    description="Returns API service operational status, version, and environment configuration."
)
def get_health():
    return HealthResponse(
        status="healthy",
        application=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT
    )


@router.get(
    "/models/status",
    response_model=ModelsStatusResponse,
    summary="Machine Learning Models Operational Status",
    description="Verifies and returns the actual runtime loading status and inference latency of the three AI subsystems."
)
def get_models_status():
    status = model_manager.get_status()
    return ModelsStatusResponse(
        crop_recommendation=status["crop_recommendation"],
        price_forecasting=status["price_forecasting"],
        yield_forecasting=status["yield_forecasting"],
        details=status["details"]
    )
