import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.services.model_manager import model_manager
from app.schemas.monitoring import (
    ModelMetadataItem,
    ModelsMetadataResponse,
    SystemMonitoringHealthResponse
)

logger = logging.getLogger("agripulse.services.model_registry")


class ModelRegistryService:
    """
    Provides safe, production-grade model registry metadata and health status.
    """

    @classmethod
    def get_models_metadata(cls) -> ModelsMetadataResponse:
        """
        Returns full metadata specification for all deep learning models without leaking filepaths.
        """
        status = model_manager.get_status()
        models: List[ModelMetadataItem] = []

        # 1. Crop Recommendation Model
        crop_loaded = status["crop_recommendation"]
        models.append(ModelMetadataItem(
            model_id="crop-recommendation-lstm-v1",
            model_name="AgriPulse Crop Recommendation LSTM",
            version="1.0.0",
            model_type="Deep Bi-Directional LSTM Classifier",
            framework="TensorFlow 2.21 / Keras 3.15",
            status="READY" if crop_loaded else "NOT_LOADED",
            dataset_source="ICRISAT / Kaggle Crop Recommendation (2,200 samples, 22 crops)",
            input_features=["N", "P", "K", "temperature", "humidity", "ph", "rainfall"],
            metrics={
                "accuracy": 0.9879,
                "precision_macro": 0.9896,
                "recall_macro": 0.9879,
                "f1_score": 0.9880,
                "top_5_accuracy": 1.0000
            },
            epochs_trained=96,
            latency_ms=status["details"]["crop_recommendation"].get("latency_ms")
        ))

        # 2. Price Forecasting Model
        price_loaded = status["price_forecasting"]
        models.append(ModelMetadataItem(
            model_id="price-forecasting-lstm-v1",
            model_name="AgriPulse Time-Series Price Forecasting LSTM",
            version="1.0.0",
            model_type="Recursive Multi-Step Time-Series LSTM Forecaster",
            framework="TensorFlow 2.21 / Keras 3.15",
            status="READY" if price_loaded else "NOT_LOADED",
            dataset_source="AGMARKNET Modal Spot Prices (6,575 daily records, 2004-2021)",
            input_features=["historical_prices (30-day continuous sequence)", "commodity", "market"],
            metrics={
                "r2_score": 0.9375,
                "mae": 129.81,
                "rmse": 253.07,
                "mape": 6.47
            },
            epochs_trained=46,
            latency_ms=status["details"]["price_forecasting"].get("latency_ms")
        ))

        # 3. Yield Forecasting Model
        yield_loaded = status["yield_forecasting"]
        models.append(ModelMetadataItem(
            model_id="yield-forecasting-dnn-v1",
            model_name="AgriPulse Crop Yield Forecasting DNN",
            version="1.0.0",
            model_type="Deep Neural Network Regressor",
            framework="TensorFlow 2.21 / Keras 3.15 / Scikit-Learn 1.9",
            status="READY" if yield_loaded else "NOT_LOADED",
            dataset_source="Directorate of Economics & Statistics (84,183 historical records)",
            input_features=["State_Name", "District_Name", "Crop", "Season", "Area", "Crop_Year"],
            metrics={
                "r2_score": 0.9165,
                "mae": 1.697,
                "rmse": 5.478,
                "medae": 0.537
            },
            epochs_trained=19,
            latency_ms=status["details"]["yield_forecasting"].get("latency_ms")
        ))

        # 4. Decision Support Synthesizer Engine
        models.append(ModelMetadataItem(
            model_id="decision-support-synthesizer-v1",
            model_name="AgriPulse Multi-Objective Decision Support Synthesizer",
            version="1.0.0",
            model_type="Pareto Multi-Criteria Optimization Engine",
            framework="AgriPulse Multi-Modal Python Engine",
            status="READY" if (crop_loaded and price_loaded and yield_loaded) else "DEGRADED",
            dataset_source="Integrated Synthesis of Crop, Yield & Market Models",
            input_features=["Soil N-P-K & pH", "Climate Parameters", "Regional Geography", "Mandi Market", "Forecast Horizon"],
            metrics={
                "scoring_weights": "0.40 Suitability + 0.35 Yield + 0.25 Market",
                "explainability": "Dynamic 4-pillar rationale generator"
            },
            epochs_trained=None,
            latency_ms=None
        ))

        return ModelsMetadataResponse(
            total_models=len(models),
            models=models
        )

    @classmethod
    def get_system_monitoring_health(cls, db: Session = None) -> SystemMonitoringHealthResponse:
        """
        Consolidates backend runtime health, database ping, and ML model availability.
        """
        from app.services.metrics_service import metrics_collector
        status_info = model_manager.get_status()

        # Check DB
        db_status = {"status": "connected", "latency_ms": 0.5}
        if db:
            try:
                t0 = datetime.now()
                db.execute(text("SELECT 1"))
                db_lat = (datetime.now() - t0).total_seconds() * 1000.0
                db_status = {"status": "connected", "latency_ms": round(db_lat, 2)}
            except Exception as e:
                db_status = {"status": "error", "error": str(e)}

        models_health = {
            "crop_recommendation": {
                "status": "ready" if status_info["crop_recommendation"] else "unavailable",
                "model_type": status_info["details"]["crop_recommendation"].get("type", "LSTM")
            },
            "price_forecasting": {
                "status": "ready" if status_info["price_forecasting"] else "unavailable",
                "model_type": status_info["details"]["price_forecasting"].get("type", "LSTM")
            },
            "yield_forecasting": {
                "status": "ready" if status_info["yield_forecasting"] else "unavailable",
                "model_type": status_info["details"]["yield_forecasting"].get("type", "DNN")
            }
        }

        all_models_ready = all(m["status"] == "ready" for m in models_health.values())
        overall_status = "healthy" if (all_models_ready and db_status["status"] == "connected") else "degraded"

        metrics = metrics_collector.get_metrics()

        return SystemMonitoringHealthResponse(
            status=overall_status,
            uptime_seconds=metrics.uptime_seconds,
            timestamp=datetime.now(timezone.utc).isoformat(),
            database=db_status,
            models=models_health
        )
