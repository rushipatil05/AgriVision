import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.config.database import Base


class PredictionHistory(Base):
    """
    Prediction history record storing inputs, generated forecasts, and execution metadata
    across all three precision agriculture ML modules.
    """
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    prediction_type = Column(String(50), nullable=False, index=True)  # 'CROP_RECOMMENDATION', 'PRICE_FORECAST', 'YIELD_FORECAST'
    input_data = Column(JSON, nullable=False)
    prediction_result = Column(JSON, nullable=False)
    latency_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="predictions")

    def __repr__(self) -> str:
        return f"<PredictionHistory id={self.id} type='{self.prediction_type}' created_at='{self.created_at}'>"
