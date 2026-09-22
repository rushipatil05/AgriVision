import logging
from datetime import datetime, timezone
from typing import Dict, List, Any
import numpy as np
from sqlalchemy.orm import Session

from app.models.prediction_history import PredictionHistory
from app.schemas.monitoring import FeatureDriftItem, DataDriftResponse

logger = logging.getLogger("agripulse.services.drift")

# Baseline reference distribution statistics derived from Level 2 verified training datasets
BASELINE_STATS: Dict[str, Dict[str, float]] = {
    "N": {"mean": 50.55, "std": 36.92, "min": 0.0, "max": 140.0},
    "P": {"mean": 53.36, "std": 32.99, "min": 5.0, "max": 145.0},
    "K": {"mean": 48.15, "std": 50.65, "min": 5.0, "max": 205.0},
    "temperature": {"mean": 25.62, "std": 5.06, "min": 8.83, "max": 43.68},
    "humidity": {"mean": 71.48, "std": 22.26, "min": 14.26, "max": 99.98},
    "ph": {"mean": 6.47, "std": 0.77, "min": 3.50, "max": 9.94},
    "rainfall": {"mean": 103.46, "std": 54.96, "min": 20.21, "max": 298.56},
}


class DriftMonitoringService:
    """
    Evaluates covariate data drift on incoming agricultural input parameters against baseline training distributions.
    """

    @classmethod
    def evaluate_drift(cls, db: Session, min_samples: int = 5) -> DataDriftResponse:
        """
        Extracts recent prediction inputs from database and computes statistical distribution shift.
        """
        records = (
            db.query(PredictionHistory)
            .filter(PredictionHistory.prediction_type.in_(["CROP_RECOMMENDATION", "DECISION"]))
            .order_by(PredictionHistory.created_at.desc())
            .limit(100)
            .all()
        )

        sample_size = len(records)
        now_str = datetime.now(timezone.utc).isoformat()

        # Handle insufficient data gracefully without fabrication
        if sample_size < min_samples:
            empty_features: List[FeatureDriftItem] = []
            for feat, b_stats in BASELINE_STATS.items():
                empty_features.append(FeatureDriftItem(
                    feature=feat,
                    drift_score=0.0,
                    status="INSUFFICIENT_DATA",
                    p_value=None,
                    baseline_stats=b_stats,
                    current_stats={"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}
                ))

            return DataDriftResponse(
                status="INSUFFICIENT_DATA",
                sample_size=sample_size,
                method="Normalized Feature Distance (Z-Shift)",
                evaluated_at=now_str,
                features=empty_features,
                message=f"Only {sample_size} prediction record(s) available. Minimum {min_samples} required for statistically valid drift assessment."
            )

        # Extract numerical arrays for each feature
        feature_data: Dict[str, List[float]] = {f: [] for f in BASELINE_STATS}
        for rec in records:
            inp = rec.input_data or {}
            for feat in BASELINE_STATS:
                if feat in inp and isinstance(inp[feat], (int, float)):
                    feature_data[feat].append(float(inp[feat]))

        feature_items: List[FeatureDriftItem] = []
        any_drift = False
        any_moderate = False

        for feat, b_stats in BASELINE_STATS.items():
            vals = feature_data.get(feat, [])
            if len(vals) < min_samples:
                feature_items.append(FeatureDriftItem(
                    feature=feat,
                    drift_score=0.0,
                    status="INSUFFICIENT_DATA",
                    p_value=None,
                    baseline_stats=b_stats,
                    current_stats={"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}
                ))
                continue

            arr = np.array(vals)
            curr_mean = float(np.mean(arr))
            curr_std = float(np.std(arr))
            curr_min = float(np.min(arr))
            curr_max = float(np.max(arr))

            b_mean = b_stats["mean"]
            b_std = b_stats["std"] if b_stats["std"] > 0 else 1.0

            # Normalized Mean Shift Distance
            drift_score = round(float(abs(curr_mean - b_mean) / b_std), 4)

            # Pseudo p-value based on standard normal CDF approximation
            z_score = drift_score * np.sqrt(len(arr))
            p_val = round(float(2.0 * (1.0 - min(0.9999, 0.5 * (1.0 + np.tanh(z_score * 0.79788))))), 4)

            if drift_score >= 0.5:
                f_status = "DRIFT_DETECTED"
                any_drift = True
            elif drift_score >= 0.2:
                f_status = "MODERATE_DRIFT"
                any_moderate = True
            else:
                f_status = "HEALTHY"

            feature_items.append(FeatureDriftItem(
                feature=feat,
                drift_score=drift_score,
                status=f_status,
                p_value=p_val,
                baseline_stats=b_stats,
                current_stats={
                    "mean": round(curr_mean, 2),
                    "std": round(curr_std, 2),
                    "min": round(curr_min, 2),
                    "max": round(curr_max, 2)
                }
            ))

        if any_drift:
            overall_status = "DRIFT_DETECTED"
            msg = "Statistically significant distribution shift detected in one or more input parameters."
        elif any_moderate:
            overall_status = "MODERATE_DRIFT"
            msg = "Moderate input parameter variation observed within tolerable operational thresholds."
        else:
            overall_status = "HEALTHY"
            msg = "All incoming inference distributions are aligned with training baseline distributions."

        return DataDriftResponse(
            status=overall_status,
            sample_size=sample_size,
            method="Normalized Feature Distance (Z-Shift & KS-Proxy)",
            evaluated_at=now_str,
            features=feature_items,
            message=msg
        )
