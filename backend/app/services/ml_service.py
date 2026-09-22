import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.schemas.crop import CropRecommendationRequest, CropRecommendationResponse
from app.schemas.price import PriceForecastRequest, PriceForecastResponse
from app.schemas.yield_ import YieldForecastRequest, YieldForecastResponse
from app.schemas.decision import DecisionRecommendationRequest, DecisionRecommendationResponse

from app.services.crop_recommendation_service import CropRecommendationService
from app.services.price_forecasting_service import PriceForecastingService
from app.services.yield_forecasting_service import YieldForecastingService
from app.services.decision_service import DecisionService
from app.services.prediction_service import PredictionService

logger = logging.getLogger("agripulse.services.ml_orchestrator")


class MLService:
    """
    Unified ML Service Facade coordinating inference across all three AI subsystems
    and persisting prediction audit trails in the database.
    """

    @staticmethod
    def predict_crop(
        request: CropRecommendationRequest,
        db: Optional[Session] = None,
        user_id: Optional[int] = None
    ) -> CropRecommendationResponse:
        """
        Executes Crop Recommendation and records result in prediction history.
        """
        response = CropRecommendationService.recommend(request)

        if db is not None:
            try:
                PredictionService.record_prediction(
                    db=db,
                    prediction_type="CROP_RECOMMENDATION",
                    input_data=request.model_dump(),
                    prediction_result=response.model_dump(),
                    latency_ms=response.execution_time_ms,
                    user_id=user_id
                )
            except Exception as e:
                logger.warning(f"Failed to record crop prediction history: {e}")

        return response

    @staticmethod
    def forecast_price(
        request: PriceForecastRequest,
        db: Optional[Session] = None,
        user_id: Optional[int] = None
    ) -> PriceForecastResponse:
        """
        Executes Crop Market Price Forecasting and records result in prediction history.
        """
        response = PriceForecastingService.forecast(request)

        if db is not None:
            try:
                PredictionService.record_prediction(
                    db=db,
                    prediction_type="PRICE_FORECAST",
                    input_data=request.model_dump(),
                    prediction_result=response.model_dump(),
                    latency_ms=response.execution_time_ms,
                    user_id=user_id
                )
            except Exception as e:
                logger.warning(f"Failed to record price forecast history: {e}")

        return response

    @staticmethod
    def predict_yield(
        request: YieldForecastRequest,
        db: Optional[Session] = None,
        user_id: Optional[int] = None
    ) -> YieldForecastResponse:
        """
        Executes Crop Yield Forecasting and records result in prediction history.
        """
        response = YieldForecastingService.predict(request)

        if db is not None:
            try:
                PredictionService.record_prediction(
                    db=db,
                    prediction_type="YIELD_FORECAST",
                    input_data=request.model_dump(),
                    prediction_result=response.model_dump(),
                    latency_ms=response.execution_time_ms,
                    user_id=user_id
                )
            except Exception as e:
                logger.warning(f"Failed to record yield forecast history: {e}")

        return response

    @staticmethod
    def recommend_decision(
        request: DecisionRecommendationRequest,
        db: Optional[Session] = None,
        user_id: Optional[int] = None
    ) -> DecisionRecommendationResponse:
        """
        Executes Agricultural Decision Support orchestration and records result in prediction history.
        """
        return DecisionService.recommend(request=request, db=db, user_id=user_id)


# Global instance
ml_service = MLService()
