import time
import logging
from typing import Dict, Any
from app.schemas.price import (
    PriceForecastRequest,
    PriceForecastDayItem,
    PriceForecastResponse
)
from ml.price_forecasting.model.predict import predict_crop_price

logger = logging.getLogger("agripulse.services.price")


class PriceForecastingService:
    """
    Business service layer executing crop market price forecasting inference.
    """

    @staticmethod
    def forecast(request: PriceForecastRequest) -> PriceForecastResponse:
        t0 = time.time()
        logger.debug(f"Processing price forecast for {request.commodity} ({request.market}) over {request.forecast_horizon} days")

        raw_result = predict_crop_price(
            historical_prices=request.historical_prices,
            commodity=request.commodity,
            market=request.market,
            forecast_horizon=request.forecast_horizon
        )

        execution_ms = round((time.time() - t0) * 1000.0, 2)

        items = [
            PriceForecastDayItem(
                day=f["day"],
                predicted_modal_price=f["predicted_modal_price"],
                unit=f.get("unit", "INR/Quintal")
            )
            for f in raw_result["forecasts"]
        ]

        logger.info(
            f"Forecasted {request.commodity} in {request.market}: "
            f"End Price = ₹{raw_result['predicted_end_price']} ({raw_result['trend_direction']}) in {execution_ms}ms"
        )

        return PriceForecastResponse(
            commodity=raw_result["commodity"],
            market=raw_result["market"],
            forecast_horizon_days=raw_result["forecast_horizon_days"],
            last_observed_price=raw_result["last_observed_price"],
            predicted_end_price=raw_result["predicted_end_price"],
            projected_percentage_change=raw_result["projected_percentage_change"],
            trend_direction=raw_result["trend_direction"],
            forecasts=items,
            execution_time_ms=execution_ms
        )
