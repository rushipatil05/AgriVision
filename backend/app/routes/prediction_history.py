from typing import Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.user import User
from app.auth.dependencies import get_current_user
from app.schemas.common import ApiResponse
from app.schemas.prediction_history import (
    PredictionHistoryItem,
    PredictionHistoryListResponse,
    PredictionDeleteResponse
)
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="/predictions", tags=["Prediction History & Audit"])


@router.get(
    "/history",
    response_model=ApiResponse[PredictionHistoryListResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve User-Specific Prediction History",
    description="Fetches paginated historical inference records belonging strictly to the authenticated user."
)
def get_prediction_history(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Page size limit (max 100)"),
    prediction_type: Optional[str] = Query(None, description="Filter by type (CROP_RECOMMENDATION, PRICE_FORECAST, YIELD_FORECAST)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    records = PredictionService.get_history(
        db=db,
        skip=skip,
        limit=page_size,
        prediction_type=prediction_type,
        user_id=current_user.id
    )
    total = PredictionService.count_history(
        db=db,
        prediction_type=prediction_type,
        user_id=current_user.id
    )

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    items = [PredictionHistoryItem.model_validate(r) for r in records]

    return ApiResponse[PredictionHistoryListResponse](
        success=True,
        data=PredictionHistoryListResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            records=items
        )
    )


@router.delete(
    "/history/{prediction_id}",
    response_model=ApiResponse[PredictionDeleteResponse],
    status_code=status.HTTP_200_OK,
    summary="Delete User Prediction Record",
    description="Deletes a specific prediction history record belonging to the authenticated user. Returns 404 if not found or owned by another user."
)
def delete_prediction_history(
    prediction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    deleted = PredictionService.delete_user_prediction(
        db=db,
        prediction_id=prediction_id,
        user_id=current_user.id
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction record not found"
        )

    return ApiResponse[PredictionDeleteResponse](
        success=True,
        data=PredictionDeleteResponse(
            message="Prediction record deleted successfully",
            deleted_id=prediction_id
        )
    )
