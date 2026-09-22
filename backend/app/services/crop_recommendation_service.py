import time
import logging
from typing import Dict, Any
from app.schemas.crop import (
    CropRecommendationRequest,
    CropRecommendationItem,
    CropRecommendationResponse
)
from ml.crop_recommendation.model.predict import predict_crop_recommendation

logger = logging.getLogger("agripulse.services.crop")


class CropRecommendationService:
    """
    Business service layer executing AI crop recommendation inference.
    """

    @staticmethod
    def recommend(request: CropRecommendationRequest) -> CropRecommendationResponse:
        t0 = time.time()
        logger.debug(f"Processing crop recommendation for inputs: {request.model_dump()}")

        raw_preds = predict_crop_recommendation(
            n=request.N,
            p=request.P,
            k=request.K,
            temperature=request.temperature,
            humidity=request.humidity,
            ph=request.ph,
            rainfall=request.rainfall,
            top_k=request.top_k
        )

        execution_ms = round((time.time() - t0) * 1000.0, 2)
        top_crop = raw_preds[0]["crop"]
        top_confidence = raw_preds[0]["probability"]

        items = [
            CropRecommendationItem(crop=item["crop"], probability=item["probability"])
            for item in raw_preds
        ]

        logger.info(f"Recommended {top_crop} ({top_confidence * 100:.1f}%) in {execution_ms}ms")

        return CropRecommendationResponse(
            recommended_crop=top_crop,
            confidence=top_confidence,
            recommendations=items,
            execution_time_ms=execution_ms
        )
