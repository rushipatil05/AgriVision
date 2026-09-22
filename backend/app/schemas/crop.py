from typing import List
from pydantic import BaseModel, Field


class CropRecommendationRequest(BaseModel):
    """
    Input soil and climatic parameters for crop recommendation.
    """
    N: float = Field(..., ge=0.0, le=200.0, description="Nitrogen ratio in soil (0-200 kg/ha)", json_schema_extra={"example": 90.0})
    P: float = Field(..., ge=0.0, le=200.0, description="Phosphorus ratio in soil (0-200 kg/ha)", json_schema_extra={"example": 42.0})
    K: float = Field(..., ge=0.0, le=250.0, description="Potassium ratio in soil (0-250 kg/ha)", json_schema_extra={"example": 43.0})
    temperature: float = Field(..., ge=0.0, le=60.0, description="Ambient temperature in Celsius (0-60°C)", json_schema_extra={"example": 20.87})
    humidity: float = Field(..., ge=0.0, le=100.0, description="Relative humidity percentage (0-100%)", json_schema_extra={"example": 82.00})
    ph: float = Field(..., ge=3.0, le=10.0, description="Soil pH level (3.0-10.0)", json_schema_extra={"example": 6.50})
    rainfall: float = Field(..., ge=0.0, le=500.0, description="Precipitation / rainfall in mm (0-500mm)", json_schema_extra={"example": 202.93})
    top_k: int = Field(5, ge=1, le=10, description="Number of ranked crop recommendations to return", json_schema_extra={"example": 5})


class CropRecommendationItem(BaseModel):
    """
    Individual ranked crop recommendation with confidence probability.
    """
    crop: str = Field(..., description="Recommended crop species name", json_schema_extra={"example": "rice"})
    probability: float = Field(..., ge=0.0, le=1.0, description="Confidence probability (0.0 to 1.0)", json_schema_extra={"example": 0.9412})


class CropRecommendationResponse(BaseModel):
    """
    Crop Recommendation prediction result payload.
    """
    recommended_crop: str = Field(..., description="Top ranked recommended crop", json_schema_extra={"example": "rice"})
    confidence: float = Field(..., description="Confidence probability of top crop", json_schema_extra={"example": 0.9412})
    recommendations: List[CropRecommendationItem] = Field(..., description="Top-K ranked crop recommendations")
    execution_time_ms: float = Field(..., description="Inference latency in milliseconds", json_schema_extra={"example": 12.4})
