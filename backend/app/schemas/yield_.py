from typing import Optional, Literal
from pydantic import BaseModel, Field


class YieldForecastRequest(BaseModel):
    """
    Input parameters for regional Crop Yield Forecasting.
    """
    state: str = Field(..., description="Indian State or Union Territory name", json_schema_extra={"example": "Punjab"})
    district: str = Field(..., description="Agricultural district name", json_schema_extra={"example": "Ludhiana"})
    crop: str = Field(..., description="Target agricultural crop name", json_schema_extra={"example": "Wheat"})
    season: str = Field(..., description="Agricultural cropping season (Kharif, Rabi, Summer, Whole Year)", json_schema_extra={"example": "Rabi"})
    area: float = Field(..., gt=0.0, description="Cultivated land area in hectares (must be > 0)", json_schema_extra={"example": 50.0})
    crop_year: int = Field(2024, ge=1990, le=2050, description="Target cultivation year", json_schema_extra={"example": 2024})
    model_type: Literal["dnn", "tree"] = Field("dnn", description="Selected ML engine: 'dnn' (Deep Neural Network) or 'tree' (Gradient Boosting)", json_schema_extra={"example": "dnn"})


class YieldForecastResponse(BaseModel):
    """
    Crop Yield Forecasting result payload.
    """
    state: str = Field(..., json_schema_extra={"example": "Punjab"})
    district: str = Field(..., json_schema_extra={"example": "Ludhiana"})
    crop: str = Field(..., json_schema_extra={"example": "Wheat"})
    season: str = Field(..., json_schema_extra={"example": "Rabi"})
    area_hectares: float = Field(..., json_schema_extra={"example": 50.0})
    crop_year: int = Field(..., json_schema_extra={"example": 2024})
    predicted_yield_tonnes_per_hectare: float = Field(..., description="Forecasted productivity in Tonnes per Hectare", json_schema_extra={"example": 5.625})
    estimated_total_production_tonnes: float = Field(..., description="Total harvest volume: Yield × Area in metric Tonnes", json_schema_extra={"example": 281.25})
    unit: str = Field("Tonnes / Hectare", json_schema_extra={"example": "Tonnes / Hectare"})
    model_used: str = Field(..., json_schema_extra={"example": "Deep Neural Network"})
    execution_time_ms: float = Field(..., description="Inference latency in milliseconds", json_schema_extra={"example": 14.2})
