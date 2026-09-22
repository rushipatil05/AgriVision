from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ModelMetadataItem(BaseModel):
    """
    Safe public metadata for a deployed deep learning model.
    """
    model_id: str = Field(..., description="Unique model identifier")
    model_name: str = Field(..., description="Human-readable model name")
    version: str = Field(..., description="Semantic version string")
    model_type: str = Field(..., description="Architecture classification")
    framework: str = Field(..., description="Deep learning framework")
    status: str = Field(..., description="Operational loading status (READY / NOT_LOADED)")
    dataset_source: str = Field(..., description="Training dataset reference")
    input_features: List[str] = Field(default_factory=list, description="List of expected input features")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Verified model performance evaluation metrics")
    epochs_trained: Optional[int] = Field(None, description="Total training epochs executed")
    latency_ms: Optional[float] = Field(None, description="Average runtime inference latency in ms")


class ModelsMetadataResponse(BaseModel):
    """
    Full registry catalog response.
    """
    total_models: int
    models: List[ModelMetadataItem]


class EndpointMetricItem(BaseModel):
    """
    Operational latency and throughput metrics for a specific endpoint.
    """
    endpoint: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float


class ApiPerformanceMetricsResponse(BaseModel):
    """
    System runtime API performance telemetry.
    """
    uptime_seconds: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate_percentage: float
    overall_avg_latency_ms: float
    total_predictions: int
    predictions_by_type: Dict[str, int]
    endpoint_breakdown: List[EndpointMetricItem]


class SystemMonitoringHealthResponse(BaseModel):
    """
    Consolidated system and model health status.
    """
    status: str = Field(..., description="Overall system health (healthy / degraded / critical)")
    uptime_seconds: float
    timestamp: str
    database: Dict[str, Any] = Field(..., description="Database connection and health status")
    models: Dict[str, Dict[str, Any]] = Field(..., description="Individual model availability and health")


class FeatureDriftItem(BaseModel):
    """
    Data drift analysis for a single input feature.
    """
    feature: str
    drift_score: float
    status: str = Field(..., description="HEALTHY / MODERATE_DRIFT / DRIFT_DETECTED / INSUFFICIENT_DATA")
    p_value: Optional[float] = None
    baseline_stats: Dict[str, float] = Field(..., description="Reference training set mean, std, min, max")
    current_stats: Dict[str, float] = Field(..., description="Recent inference sample mean, std, min, max")


class DataDriftResponse(BaseModel):
    """
    System-wide data drift analysis response.
    """
    status: str = Field(..., description="Overall drift summary (HEALTHY / MODERATE_DRIFT / DRIFT_DETECTED / INSUFFICIENT_DATA)")
    sample_size: int = Field(..., description="Number of historical prediction samples analyzed")
    method: str = Field(..., description="Statistical test method used (e.g. KS-Test & PSI)")
    evaluated_at: str
    features: List[FeatureDriftItem]
    message: str


class CropClassFrequency(BaseModel):
    crop: str
    count: int
    percentage: float


class YieldDistributionStats(BaseModel):
    count: int
    mean_yield_tonnes_per_ha: float
    min_yield_tonnes_per_ha: float
    max_yield_tonnes_per_ha: float
    median_yield_tonnes_per_ha: float


class PriceTrendFrequency(BaseModel):
    trend: str
    count: int
    percentage: float


class DecisionScoreDistributionStats(BaseModel):
    count: int
    mean_score: float
    min_score: float
    max_score: float
    median_score: float


class PredictionDistributionResponse(BaseModel):
    """
    Aggregated prediction output distribution report.
    """
    status: str = Field(..., description="DATA_AVAILABLE or INSUFFICIENT_DATA")
    total_predictions: int
    crop_recommendations: Optional[List[CropClassFrequency]] = None
    yield_forecasting: Optional[YieldDistributionStats] = None
    price_forecasting: Optional[List[PriceTrendFrequency]] = None
    decision_support: Optional[DecisionScoreDistributionStats] = None
    message: str
