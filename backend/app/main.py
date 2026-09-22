import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.config.database import init_db
from app.routes import api_router
from app.services.model_manager import model_manager

# Configure structured logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("agripulse.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager:
    - On Startup: Initializes database schema and pre-loads all ML model artifacts.
    - On Shutdown: Cleans up resources.
    """
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} ({settings.ENVIRONMENT})...")
    
    # 1. Initialize Database Tables
    try:
        init_db()
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.warning(f"Database auto-initialization skipped or failed: {e}")
        
    # 2. Pre-load Machine Learning Models into memory
    t0 = time.time()
    model_manager.initialize_models()
    total_startup_ms = round((time.time() - t0) * 1000.0, 2)
    logger.info(f"All ML Subsystems initialized in {total_startup_ms}ms")
    
    yield
    
    logger.info(f"Shutting down {settings.APP_NAME}...")


tags_metadata = [
    {
        "name": "Authentication & User Management",
        "description": "User registration, authentication login, profile retrieval, and token lifecycle management.",
    },
    {
        "name": "Crop Recommendation AI",
        "description": "LSTM-based crop suitability recommendation based on soil nutrient and environmental parameters.",
    },
    {
        "name": "Price Forecasting AI",
        "description": "Time-Series LSTM commodity modal price forecasting across 1, 7, and 30-day forecast horizons.",
    },
    {
        "name": "Crop Yield Forecasting AI",
        "description": "Deep Neural Network regression for regional crop yield and total harvest volume estimation.",
    },
    {
        "name": "Prediction History & Audit",
        "description": "User-isolated historical inference log retrieval, pagination, and record deletion.",
    },
    {
        "name": "Decision Support AI",
        "description": "Integrated multi-modal agricultural decision engine synthesizing crop, price, and yield models.",
    },
    {
        "name": "MLOps & System Monitoring",
        "description": "Model registry, live performance telemetry, data drift, and prediction distribution analytics.",
    },
    {
        "name": "System",
        "description": "Health checks and ML runtime diagnostic endpoints.",
    }
]

# Create FastAPI Application Instance
app = FastAPI(
    title=f"{settings.APP_NAME} - Precision Agriculture AI Platform",
    version=settings.APP_VERSION,
    description=(
        "Production REST API for AgriPulse: Providing deep learning-powered crop recommendation, "
        "crop market price forecasting, regional crop yield estimation, decision support, and secure user management."
    ),
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.services.metrics_service import metrics_collector

@app.middleware("http")
async def telemetry_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000.0, 2)
    metrics_collector.record_request(request.url.path, response.status_code, duration_ms)
    return response


# Centralized Error Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handles Pydantic request body validation failures with standardized 422 JSON response.
    """
    errors = []
    for err in exc.errors():
        field_loc = " -> ".join(str(loc) for loc in err.get("loc", []))
        errors.append({
            "field": field_loc,
            "message": err.get("msg"),
            "type": err.get("type")
        })
    logger.warning(f"Validation error on {request.method} {request.url.path}: {errors}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The submitted request data failed schema validation.",
                "details": errors
            }
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """
    Handles domain logic / agronomic constraint validation failures with 400 Bad Request.
    """
    logger.warning(f"Bad request on {request.method} {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": str(exc)
            }
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handles standard HTTP exceptions with unified error payload format.
    """
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "success": False,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail
            }
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Catches all unexpected internal server errors without leaking internal stack traces.
    """
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred while processing the request."
            }
        }
    )


# Mount API Routers
app.include_router(api_router, prefix="/api")


# Top-level Convenience Routes
@app.get("/api/health", tags=["System"])
def legacy_health():
    """Top-level health check endpoint."""
    return {
        "status": "healthy",
        "service": "AgriPulse Precision Agriculture API",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/", tags=["System"])
def root():
    """API root landing endpoint."""
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "health": "/api/v1/health",
        "model_status": "/api/v1/models/status"
    }
