import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.prediction_history import PredictionHistory

logger = logging.getLogger("agripulse.services.prediction_history")


class PredictionService:
    """
    Database persistence service for recording, querying, and managing prediction histories.
    """

    @staticmethod
    def record_prediction(
        db: Session,
        prediction_type: str,
        input_data: Dict[str, Any],
        prediction_result: Dict[str, Any],
        latency_ms: Optional[float] = None,
        user_id: Optional[int] = None
    ) -> PredictionHistory:
        """
        Records a completed prediction into the database history table.
        """
        try:
            record = PredictionHistory(
                user_id=user_id,
                prediction_type=prediction_type,
                input_data=input_data,
                prediction_result=prediction_result,
                latency_ms=latency_ms
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            logger.debug(f"Saved prediction history record id={record.id} type={prediction_type} user_id={user_id}")
            return record
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save prediction history record: {e}", exc_info=True)
            raise

    @staticmethod
    def get_history(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        prediction_type: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> List[PredictionHistory]:
        """
        Queries recent prediction history records for a specific user (or global audit if None).
        """
        query = db.query(PredictionHistory)
        if user_id is not None:
            query = query.filter(PredictionHistory.user_id == user_id)
        if prediction_type:
            query = query.filter(PredictionHistory.prediction_type == prediction_type)
        return query.order_by(PredictionHistory.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def count_history(
        db: Session,
        prediction_type: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> int:
        """
        Returns total count of prediction history records for a specific user.
        """
        query = db.query(PredictionHistory)
        if user_id is not None:
            query = query.filter(PredictionHistory.user_id == user_id)
        if prediction_type:
            query = query.filter(PredictionHistory.prediction_type == prediction_type)
        return query.count()

    @staticmethod
    def delete_user_prediction(
        db: Session,
        prediction_id: int,
        user_id: int
    ) -> bool:
        """
        Deletes a prediction record strictly owned by the specified user.
        Returns True if found and deleted, False otherwise (no leakage of other users' records).
        """
        record = db.query(PredictionHistory).filter(
            PredictionHistory.id == prediction_id,
            PredictionHistory.user_id == user_id
        ).first()

        if not record:
            return False

        try:
            db.delete(record)
            db.commit()
            logger.info(f"Deleted prediction history record id={prediction_id} for user_id={user_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete prediction history record: {e}", exc_info=True)
            raise
