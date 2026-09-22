import time
import logging
from typing import Dict, Any
from app.schemas.yield_ import (
    YieldForecastRequest,
    YieldForecastResponse
)
from ml.yield_forecasting.model.predict import predict_crop_yield

logger = logging.getLogger("agripulse.services.yield")


class YieldForecastingService:
    """
    Business service layer executing crop yield forecasting inference.
    """

    @staticmethod
    def predict(request: YieldForecastRequest) -> YieldForecastResponse:
        t0 = time.time()
        logger.debug(
            f"Processing yield forecast for {request.crop} in {request.district}, {request.state} "
            f"({request.area} ha, Season: {request.season}, Year: {request.crop_year})"
        )

        raw_result = predict_crop_yield(
            state=request.state,
            district=request.district,
            crop=request.crop,
            season=request.season,
            area=request.area,
            crop_year=request.crop_year,
            model_type=request.model_type
        )

        execution_ms = round((time.time() - t0) * 1000.0, 2)

        logger.info(
            f"Predicted {request.crop} Yield: {raw_result['predicted_yield_tonnes_per_hectare']} t/ha "
            f"(Total: {raw_result['estimated_total_production_tonnes']} tonnes) via {raw_result['model_used']} in {execution_ms}ms"
        )

        return YieldForecastResponse(
            state=raw_result["state"],
            district=raw_result["district"],
            crop=raw_result["crop"],
            season=raw_result["season"],
            area_hectares=raw_result["area_hectares"],
            crop_year=raw_result["crop_year"],
            predicted_yield_tonnes_per_hectare=raw_result["predicted_yield_tonnes_per_hectare"],
            estimated_total_production_tonnes=raw_result["estimated_total_production_tonnes"],
            unit=raw_result["unit"],
            model_used=raw_result["model_used"],
            execution_time_ms=execution_ms
        )
