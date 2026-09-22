from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.user import User
from app.auth.dependencies import get_optional_current_user
from app.schemas.common import ApiResponse
from app.schemas.yield_ import YieldForecastRequest, YieldForecastResponse
from app.services.ml_service import ml_service

router = APIRouter(prefix="/yield", tags=["Crop Yield Forecasting AI"])


@router.post(
    "/predict",
    response_model=ApiResponse[YieldForecastResponse],
    status_code=status.HTTP_200_OK,
    summary="Predict Regional Agricultural Crop Yield",
    description=(
        "Estimates agricultural crop yield productivity (Tonnes / Hectare) and total harvest output "
        "based on regional State, District, Season, Crop, Year, and Land Area using a Deep Neural Network regressor."
    )
)
def predict_yield(
    request: YieldForecastRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else None
    result = ml_service.predict_yield(request=request, db=db, user_id=user_id)
    return ApiResponse[YieldForecastResponse](
        success=True,
        data=result
    )
