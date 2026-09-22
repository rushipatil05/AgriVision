from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.user import User
from app.auth.dependencies import get_optional_current_user
from app.schemas.common import ApiResponse
from app.schemas.crop import CropRecommendationRequest, CropRecommendationResponse
from app.services.ml_service import ml_service

router = APIRouter(prefix="/crop", tags=["Crop Recommendation AI"])


@router.post(
    "/recommend",
    response_model=ApiResponse[CropRecommendationResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate AI Crop Recommendations",
    description=(
        "Analyzes soil nutrient parameters (Nitrogen, Phosphorus, Potassium, pH) "
        "and environmental climate conditions (Temperature, Humidity, Rainfall) "
        "to output top-ranked crop recommendations using a trained LSTM Neural Network."
    )
)
def recommend_crop(
    request: CropRecommendationRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else None
    result = ml_service.predict_crop(request=request, db=db, user_id=user_id)
    return ApiResponse[CropRecommendationResponse](
        success=True,
        data=result
    )
