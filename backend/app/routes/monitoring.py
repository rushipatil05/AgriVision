import logging
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.monitoring import (
    ModelsMetadataResponse,
    ApiPerformanceMetricsResponse,
    SystemMonitoringHealthResponse,
    DataDriftResponse,
    PredictionDistributionResponse
)
from app.services.model_registry_service import ModelRegistryService
from app.services.metrics_service import metrics_collector
from app.services.drift_service import DriftMonitoringService
from app.services.distribution_service import PredictionDistributionService

logger = logging.getLogger("agripulse.routes.monitoring")

router = APIRouter(prefix="/monitoring", tags=["MLOps & System Monitoring"])


@router.get(
    "/models",
    response_model=ApiResponse[ModelsMetadataResponse],
    status_code=status.HTTP_200_OK,
    summary="Model Registry & Metadata Catalog",
    description="Returns public metadata, versions, training datasets, input features, and verified evaluation metrics for all deployed ML models."
)
def get_models_metadata():
    metadata = ModelRegistryService.get_models_metadata()
    return ApiResponse[ModelsMetadataResponse](
        success=True,
        data=metadata
    )


@router.get(
    "/metrics",
    response_model=ApiResponse[ApiPerformanceMetricsResponse],
    status_code=status.HTTP_200_OK,
    summary="API & Model Performance Telemetry",
    description="Returns live in-memory operational metrics including total requests, success/error rates, latency percentiles, and predictions by subsystem."
)
def get_performance_metrics():
    metrics = metrics_collector.get_metrics()
    return ApiResponse[ApiPerformanceMetricsResponse](
        success=True,
        data=metrics
    )


@router.get(
    "/health",
    response_model=ApiResponse[SystemMonitoringHealthResponse],
    status_code=status.HTTP_200_OK,
    summary="Consolidated System & Subsystem Health",
    description="Provides real-time health diagnostics across the API server, database connectivity, and preloaded neural network artifacts."
)
def get_monitoring_health(db: Session = Depends(get_db)):
    health_report = ModelRegistryService.get_system_monitoring_health(db=db)
    return ApiResponse[SystemMonitoringHealthResponse](
        success=True,
        data=health_report
    )


@router.get(
    "/drift",
    response_model=ApiResponse[DataDriftResponse],
    status_code=status.HTTP_200_OK,
    summary="Data Drift & Covariate Shift Analysis",
    description="Evaluates input feature distributions (N, P, K, climate) from recent inference logs against baseline training distributions."
)
def get_data_drift(
    min_samples: int = Query(5, ge=1, le=100, description="Minimum samples required for drift calculation"),
    db: Session = Depends(get_db)
):
    drift_report = DriftMonitoringService.evaluate_drift(db=db, min_samples=min_samples)
    return ApiResponse[DataDriftResponse](
        success=True,
        data=drift_report
    )


@router.get(
    "/distributions",
    response_model=ApiResponse[PredictionDistributionResponse],
    status_code=status.HTTP_200_OK,
    summary="Prediction Output Distribution Monitoring",
    description="Analyzes recorded prediction outputs to monitor recommended crop frequencies, predicted yield ranges, price trends, and decision scores."
)
def get_prediction_distributions(db: Session = Depends(get_db)):
    dist_report = PredictionDistributionService.analyze_distributions(db=db)
    return ApiResponse[PredictionDistributionResponse](
        success=True,
        data=dist_report
    )
