from typing import Generic, TypeVar, Optional, Any, Dict
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ErrorDetail(BaseModel):
    """
    Structured error payload for API error responses.
    """
    code: str = Field(..., description="Machine-readable error code", json_schema_extra={"example": "INVALID_INPUT"})
    message: str = Field(..., description="Human-readable error explanation", json_schema_extra={"example": "Input N must be between 0 and 200"})
    details: Optional[Any] = Field(None, description="Optional extra error context")


class ApiResponse(BaseModel, Generic[DataT]):
    """
    Unified standard API response wrapper.
    """
    success: bool = Field(True, description="Indicates whether the request completed successfully")
    message: Optional[str] = Field(None, description="Optional status message")
    data: Optional[DataT] = Field(None, description="Response payload data")
    error: Optional[ErrorDetail] = Field(None, description="Error detail if success is False")


class HealthResponse(BaseModel):
    """
    Service health check payload.
    """
    status: str = Field("healthy", json_schema_extra={"example": "healthy"})
    application: str = Field("AgriPulse", json_schema_extra={"example": "AgriPulse"})
    version: str = Field("0.1.0", json_schema_extra={"example": "0.1.0"})
    environment: str = Field("development", json_schema_extra={"example": "development"})


class ModelStatusItem(BaseModel):
    """
    Individual model status details.
    """
    status: str = Field(..., json_schema_extra={"example": "loaded"})
    model_type: str = Field(..., json_schema_extra={"example": "LSTM Neural Network"})
    artifact_path: str = Field(..., json_schema_extra={"example": "ml/crop_recommendation/model/crop_recommendation_lstm.keras"})
    latency_ms: Optional[float] = Field(None, json_schema_extra={"example": 45.2})


class ModelsStatusResponse(BaseModel):
    """
    Status of all three integrated ML subsystems.
    """
    crop_recommendation: str = Field(..., json_schema_extra={"example": "loaded"})
    price_forecasting: str = Field(..., json_schema_extra={"example": "loaded"})
    yield_forecasting: str = Field(..., json_schema_extra={"example": "loaded"})
    details: Dict[str, ModelStatusItem]
