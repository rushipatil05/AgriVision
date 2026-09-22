import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class PredictionHistoryItem(BaseModel):
    """
    Representation of a historical prediction record.
    """
    id: int
    user_id: Optional[int] = None
    prediction_type: str
    input_data: Dict[str, Any]
    prediction_result: Dict[str, Any]
    latency_ms: Optional[float] = None
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class PredictionHistoryListResponse(BaseModel):
    """
    Paginated list of prediction history records.
    """
    total: int = Field(..., json_schema_extra={"example": 25})
    page: Optional[int] = Field(default=1, json_schema_extra={"example": 1})
    page_size: Optional[int] = Field(default=20, json_schema_extra={"example": 20})
    total_pages: Optional[int] = Field(default=1, json_schema_extra={"example": 2})
    records: List[PredictionHistoryItem]


class PredictionDeleteResponse(BaseModel):
    """
    Response model for prediction deletion.
    """
    message: str = Field(default="Prediction record deleted successfully")
    deleted_id: int
