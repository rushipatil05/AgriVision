from typing import List, Literal
from pydantic import BaseModel, Field, field_validator


class PriceForecastRequest(BaseModel):
    """
    Input request for Crop Market Price Forecasting.
    """
    commodity: str = Field("Onion", description="Target agricultural commodity name", json_schema_extra={"example": "Onion"})
    market: str = Field("Lasalgaon", description="Target APMC wholesale mandi market", json_schema_extra={"example": "Lasalgaon"})
    historical_prices: List[float] = Field(
        ...,
        min_length=30,
        description="Chronological historical daily modal prices (minimum 30 continuous observations)",
        json_schema_extra={"example": [1200.0 + i * 15 for i in range(30)]}
    )
    forecast_horizon: Literal[1, 7, 14, 30] = Field(
        7,
        description="Forecast horizon in days (supported: 1, 7, 14, 30)",
        json_schema_extra={"example": 7}
    )

    @field_validator("historical_prices")
    @classmethod
    def validate_prices(cls, v: List[float]) -> List[float]:
        if len(v) < 30:
            raise ValueError("historical_prices must contain at least 30 continuous daily observations.")
        for idx, p in enumerate(v):
            if p <= 0:
                raise ValueError(f"Historical price at index {idx} must be strictly positive (got {p}).")
        return v


class PriceForecastDayItem(BaseModel):
    """
    Daily price forecast item.
    """
    day: int = Field(..., description="Day index of the forecast horizon", json_schema_extra={"example": 1})
    predicted_modal_price: float = Field(..., description="Forecasted modal spot price in INR per Quintal", json_schema_extra={"example": 1638.93})
    unit: str = Field("INR/Quintal", description="Currency per weight unit", json_schema_extra={"example": "INR/Quintal"})


class PriceForecastResponse(BaseModel):
    """
    Price forecast result payload.
    """
    commodity: str = Field(..., json_schema_extra={"example": "Onion"})
    market: str = Field(..., json_schema_extra={"example": "Lasalgaon"})
    forecast_horizon_days: int = Field(..., json_schema_extra={"example": 7})
    last_observed_price: float = Field(..., description="Most recent historical price observation", json_schema_extra={"example": 1645.0})
    predicted_end_price: float = Field(..., description="Forecasted price at the end of the horizon", json_schema_extra={"example": 1547.54})
    projected_percentage_change: float = Field(..., description="Expected price percentage change over horizon", json_schema_extra={"example": -5.92})
    trend_direction: str = Field(..., description="Projected price trajectory (UPWARD, DOWNWARD, STABLE)", json_schema_extra={"example": "DOWNWARD"})
    forecasts: List[PriceForecastDayItem] = Field(..., description="Day-by-day forecasted price sequence")
    execution_time_ms: float = Field(..., description="Inference latency in milliseconds", json_schema_extra={"example": 28.5})
