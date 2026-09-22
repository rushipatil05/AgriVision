from fastapi import APIRouter
from app.routes.health import router as health_router
from app.routes.auth import router as auth_router
from app.routes.crop import router as crop_router
from app.routes.price import router as price_router
from app.routes.yield_ import router as yield_router
from app.routes.decision import router as decision_router
from app.routes.prediction_history import router as history_router
from app.routes.monitoring import router as monitoring_router

api_router = APIRouter(prefix="/v1")

# Mount sub-routers
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(crop_router)
api_router.include_router(price_router)
api_router.include_router(yield_router)
api_router.include_router(decision_router)
api_router.include_router(history_router)
api_router.include_router(monitoring_router)

__all__ = ["api_router"]
