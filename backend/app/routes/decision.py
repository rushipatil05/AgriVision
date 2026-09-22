from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.user import User
from app.auth.dependencies import get_optional_current_user
from app.schemas.common import ApiResponse
from app.schemas.decision import DecisionRecommendationRequest, DecisionRecommendationResponse
from app.services.ml_service import ml_service

router = APIRouter(prefix="/decision", tags=["AI Agricultural Decision Support"])


@router.post(
    "/recommend",
    response_model=ApiResponse[DecisionRecommendationResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate Agricultural Decision Support Recommendations",
    description=(
        "Orchestrates deep learning crop suitability, neural harvest yield projections, "
        "and market price trajectories to rank and recommend optimal crops with transparent "
        "decision scoring and dynamic explainability rationale."
    )
)
def recommend_agricultural_decision(
    request: DecisionRecommendationRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else None
    result = ml_service.recommend_decision(request=request, db=db, user_id=user_id)
    return ApiResponse[DecisionRecommendationResponse](
        success=True,
        data=result
    )
