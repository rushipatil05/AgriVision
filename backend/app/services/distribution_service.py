import logging
from typing import Dict, List, Any, Optional
import numpy as np
from sqlalchemy.orm import Session

from app.models.prediction_history import PredictionHistory
from app.schemas.monitoring import (
    PredictionDistributionResponse,
    CropClassFrequency,
    YieldDistributionStats,
    PriceTrendFrequency,
    DecisionScoreDistributionStats
)

logger = logging.getLogger("agripulse.services.distribution")


class PredictionDistributionService:
    """
    Monitors and aggregates output prediction distributions across all model subsystems.
    """

    @classmethod
    def analyze_distributions(cls, db: Session) -> PredictionDistributionResponse:
        """
        Extracts prediction history and summarizes output frequency and descriptive metrics.
        """
        records = db.query(PredictionHistory).order_by(PredictionHistory.created_at.desc()).limit(200).all()
        total_preds = len(records)

        if total_preds == 0:
            return PredictionDistributionResponse(
                status="INSUFFICIENT_DATA",
                total_predictions=0,
                crop_recommendations=None,
                yield_forecasting=None,
                price_forecasting=None,
                decision_support=None,
                message="No prediction records logged yet in prediction history."
            )

        # 1. Crop Recommendations Breakdown
        crop_counts: Dict[str, int] = {}
        for r in records:
            res = r.prediction_result or {}
            crop_name = res.get("recommended_crop")
            if crop_name:
                crop_counts[crop_name] = crop_counts.get(crop_name, 0) + 1

        crop_total = sum(crop_counts.values())
        crop_freqs: List[CropClassFrequency] = []
        for c_name, c_cnt in sorted(crop_counts.items(), key=lambda x: x[1], reverse=True):
            crop_freqs.append(CropClassFrequency(
                crop=c_name,
                count=c_cnt,
                percentage=round((c_cnt / crop_total * 100.0), 1) if crop_total > 0 else 0.0
            ))

        # 2. Yield Forecasting Distribution
        yield_vals: List[float] = []
        for r in records:
            res = r.prediction_result or {}
            y_val = res.get("predicted_yield_tonnes_per_hectare") or res.get("predicted_yield")
            if y_val is not None and isinstance(y_val, (int, float)):
                yield_vals.append(float(y_val))

        yield_stats: Optional[YieldDistributionStats] = None
        if yield_vals:
            arr_y = np.array(yield_vals)
            yield_stats = YieldDistributionStats(
                count=len(yield_vals),
                mean_yield_tonnes_per_ha=round(float(np.mean(arr_y)), 2),
                min_yield_tonnes_per_ha=round(float(np.min(arr_y)), 2),
                max_yield_tonnes_per_ha=round(float(np.max(arr_y)), 2),
                median_yield_tonnes_per_ha=round(float(np.median(arr_y)), 2)
            )

        # 3. Price Forecasting Trend Breakdown
        trend_counts: Dict[str, int] = {}
        for r in records:
            res = r.prediction_result or {}
            trend = res.get("trend_direction") or res.get("price_trend")
            if trend:
                trend_upper = str(trend).upper()
                trend_counts[trend_upper] = trend_counts.get(trend_upper, 0) + 1

        trend_total = sum(trend_counts.values())
        price_freqs: List[PriceTrendFrequency] = []
        for t_name, t_cnt in trend_counts.items():
            price_freqs.append(PriceTrendFrequency(
                trend=t_name,
                count=t_cnt,
                percentage=round((t_cnt / trend_total * 100.0), 1) if trend_total > 0 else 0.0
            ))

        # 4. Decision Support Scores Breakdown
        score_vals: List[float] = []
        for r in records:
            if r.prediction_type.upper() == "DECISION":
                res = r.prediction_result or {}
                d_score = res.get("decision_score")
                if d_score is not None and isinstance(d_score, (int, float)):
                    score_vals.append(float(d_score))

        decision_stats: Optional[DecisionScoreDistributionStats] = None
        if score_vals:
            arr_s = np.array(score_vals)
            decision_stats = DecisionScoreDistributionStats(
                count=len(score_vals),
                mean_score=round(float(np.mean(arr_s)), 1),
                min_score=round(float(np.min(arr_s)), 1),
                max_score=round(float(np.max(arr_s)), 1),
                median_score=round(float(np.median(arr_s)), 1)
            )

        return PredictionDistributionResponse(
            status="DATA_AVAILABLE",
            total_predictions=total_preds,
            crop_recommendations=crop_freqs if crop_freqs else None,
            yield_forecasting=yield_stats,
            price_forecasting=price_freqs if price_freqs else None,
            decision_support=decision_stats,
            message=f"Distribution analysis generated across {total_preds} logged historical inferences."
        )
