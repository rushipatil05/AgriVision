from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.user import User
from app.auth.dependencies import get_optional_current_user
from app.schemas.common import ApiResponse
from app.schemas.price import PriceForecastRequest, PriceForecastResponse
from app.services.ml_service import ml_service

router = APIRouter(prefix="/price", tags=["Price Forecasting AI"])


@router.post(
    "/forecast",
    response_model=ApiResponse[PriceForecastResponse],
    status_code=status.HTTP_200_OK,
    summary="Forecast Agricultural Commodity Market Prices",
    description=(
        "Processes historical daily modal price sequences (lookback of 30 days) to generate "
        "multi-step future spot price forecasts (1, 7, or 30 days ahead) using a trained Time-Series LSTM model."
    )
)
def forecast_price(
    request: PriceForecastRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else None
    result = ml_service.forecast_price(request=request, db=db, user_id=user_id)
    return ApiResponse[PriceForecastResponse](
        success=True,
        data=result
    )
