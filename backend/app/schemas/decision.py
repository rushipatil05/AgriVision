from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator


class DecisionRecommendationRequest(BaseModel):
    """
    Unified input payload for the AI Agricultural Decision Support System.
    Combines soil, climatic, regional farming, and market parameters.
    """
    # Soil & Environmental Parameters (Crop Recommendation)
    N: float = Field(..., ge=0.0, le=200.0, description="Nitrogen ratio in soil (0-200 kg/ha)", json_schema_extra={"example": 90.0})
    P: float = Field(..., ge=0.0, le=200.0, description="Phosphorus ratio in soil (0-200 kg/ha)", json_schema_extra={"example": 42.0})
    K: float = Field(..., ge=0.0, le=250.0, description="Potassium ratio in soil (0-250 kg/ha)", json_schema_extra={"example": 43.0})
    temperature: float = Field(..., ge=0.0, le=60.0, description="Ambient temperature in Celsius (0-60°C)", json_schema_extra={"example": 20.87})
    humidity: float = Field(..., ge=0.0, le=100.0, description="Relative humidity percentage (0-100%)", json_schema_extra={"example": 82.00})
    ph: float = Field(..., ge=3.0, le=10.0, description="Soil pH level (3.0-10.0)", json_schema_extra={"example": 6.50})
    rainfall: float = Field(..., ge=0.0, le=500.0, description="Precipitation in mm (0-500mm)", json_schema_extra={"example": 202.93})

    # Regional Farming Parameters (Yield Forecasting)
    state: str = Field("Punjab", description="State or Union Territory name", json_schema_extra={"example": "Punjab"})
    district: str = Field("Ludhiana", description="Agricultural district name", json_schema_extra={"example": "Ludhiana"})
    season: str = Field("Rabi", description="Agricultural season (Kharif, Rabi, Summer, Whole Year)", json_schema_extra={"example": "Rabi"})
    area: float = Field(10.0, gt=0.0, description="Cultivated area in hectares", json_schema_extra={"example": 10.0})
    crop_year: int = Field(2024, ge=1990, le=2050, description="Cultivation year", json_schema_extra={"example": 2024})

    # Market Parameters (Price Forecasting)
    market: str = Field("Azadpur", description="Target APMC wholesale mandi", json_schema_extra={"example": "Azadpur"})
    forecast_horizon: Literal[1, 7, 30] = Field(7, description="Price forecast horizon in days", json_schema_extra={"example": 7})
    historical_prices: Optional[List[float]] = Field(
        None,
        description="Optional 30-day historical modal prices sequence. If omitted, realistic commodity baseline is derived automatically."
    )

    @field_validator("historical_prices")
    @classmethod
    def validate_historical_prices(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        if v is not None:
            if len(v) < 30:
                raise ValueError("historical_prices must contain at least 30 continuous daily observations if provided.")
            for p in v:
                if p <= 0:
                    raise ValueError(f"Historical prices must be positive, got {p}")
        return v


class AlternativeCropEvaluation(BaseModel):
    """
    Multi-dimensional evaluation and scoring metrics for a candidate crop.
    """
    crop: str = Field(..., description="Crop variety name")
    rank: int = Field(..., description="Decision ranking position (1 = Best)")
    decision_score: float = Field(..., description="Overall Agricultural Decision Score (0 - 100)")
    suitability_probability: float = Field(..., description="ML Crop Recommendation model probability (0.0 - 1.0)")
    suitability_score: float = Field(..., description="Normalized Suitability indicator (0 - 100)")
    predicted_yield_tonnes_per_hectare: float = Field(..., description="Predicted harvest productivity in t/ha")
    estimated_total_production_tonnes: float = Field(..., description="Estimated total harvest volume in metric tonnes")
    yield_score: float = Field(..., description="Normalized Yield productivity indicator (0 - 100)")
    forecasted_market_price: float = Field(..., description="Forecasted terminal wholesale price in INR/Quintal")
    price_trend: str = Field(..., description="Market price trend trajectory (UPWARD, DOWNWARD, STABLE)")
    market_score: float = Field(..., description="Normalized Market opportunity indicator (0 - 100)")


class DecisionExplanation(BaseModel):
    """
    Dynamically generated explainability breakdown for the recommended crop decision.
    """
    summary: str = Field(..., description="Executive summary of the agricultural decision")
    soil_compatibility: str = Field(..., description="Evaluation of soil N-P-K and pH suitability")
    climatic_suitability: str = Field(..., description="Evaluation of temperature, humidity, and rainfall alignment")
    yield_potential: str = Field(..., description="Analysis of projected yield in the target district/season")
    market_outlook: str = Field(..., description="Analysis of expected mandi price movements and trend")
    key_advantages: List[str] = Field(default_factory=list, description="Key bullet points supporting the choice")


class DecisionRecommendationResponse(BaseModel):
    """
    Comprehensive result payload of the AI Agricultural Decision Support System.
    """
    recommended_crop: str = Field(..., description="Primary recommended crop variety")
    decision_score: float = Field(..., description="Overall Decision Score for the primary crop (0 - 100)")
    crop_confidence: float = Field(..., description="Crop recommendation model confidence")
    suitability_score: float = Field(..., description="Normalized suitability score (0 - 100)")
    predicted_yield: float = Field(..., description="Predicted harvest yield in Tonnes / Hectare")
    yield_unit: str = Field("Tonnes / Hectare", description="Yield measurement unit")
    estimated_production_tonnes: float = Field(..., description="Total farm harvest volume in Tonnes")
    yield_score: float = Field(..., description="Normalized yield productivity score (0 - 100)")
    forecast_price: float = Field(..., description="Forecasted wholesale market price in INR/Quintal")
    price_unit: str = Field("INR/Quintal", description="Price unit")
    price_trend: str = Field(..., description="Projected price trajectory (UPWARD, DOWNWARD, STABLE)")
    market: str = Field(..., description="Mandi market analyzed")
    market_score: float = Field(..., description="Normalized market opportunity score (0 - 100)")
    explanation: DecisionExplanation = Field(..., description="Structured explainability breakdown")
    alternatives: List[AlternativeCropEvaluation] = Field(..., description="Ranked alternative crop comparisons")
    execution_time_ms: float = Field(..., description="Total orchestration latency in milliseconds")
