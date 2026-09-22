import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger("agripulse.model_manager")


class ModelManager:
    """
    Centralized Model Manager that loads, verifies, and caches all machine learning
    model artifacts and preprocessors during application startup.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.status: Dict[str, Dict[str, Any]] = {
            "crop_recommendation": {"status": "unloaded", "model_type": "LSTM Neural Network", "latency_ms": None},
            "price_forecasting": {"status": "unloaded", "model_type": "Time-Series LSTM", "latency_ms": None},
            "yield_forecasting": {"status": "unloaded", "model_type": "Deep Neural Network Regressor", "latency_ms": None}
        }
        self.artifacts: Dict[str, Any] = {}
        self._initialized = True

    def initialize_models(self) -> None:
        """
        Loads all three ML subsystems into memory and verifies inference capability.
        """
        logger.info("Initializing AgriPulse Machine Learning subsystems...")

        # 1. Crop Recommendation Subsystem
        try:
            t0 = time.time()
            from ml.crop_recommendation.model.predict import load_inference_artifacts as load_crop_artifacts
            self.artifacts["crop_recommendation"] = load_crop_artifacts()
            latency = round((time.time() - t0) * 1000.0, 2)
            self.status["crop_recommendation"] = {
                "status": "loaded",
                "model_type": "LSTM Neural Network",
                "artifact_path": "ml/crop_recommendation/model/crop_recommendation_lstm.keras",
                "latency_ms": latency
            }
            logger.info(f"Loaded Crop Recommendation LSTM in {latency}ms")
        except Exception as e:
            logger.error(f"Failed to load Crop Recommendation model: {e}", exc_info=True)
            self.status["crop_recommendation"] = {
                "status": f"failed: {str(e)}",
                "model_type": "LSTM Neural Network",
                "artifact_path": "ml/crop_recommendation/model/crop_recommendation_lstm.keras",
                "latency_ms": None
            }

        # 2. Price Forecasting Subsystem
        try:
            t0 = time.time()
            from ml.price_forecasting.model.predict import load_price_inference_artifacts
            self.artifacts["price_forecasting"] = load_price_inference_artifacts()
            latency = round((time.time() - t0) * 1000.0, 2)
            self.status["price_forecasting"] = {
                "status": "loaded",
                "model_type": "Time-Series LSTM",
                "artifact_path": "ml/price_forecasting/model/crop_price_lstm.keras",
                "latency_ms": latency
            }
            logger.info(f"Loaded Price Forecasting LSTM in {latency}ms")
        except Exception as e:
            logger.error(f"Failed to load Price Forecasting model: {e}", exc_info=True)
            self.status["price_forecasting"] = {
                "status": f"failed: {str(e)}",
                "model_type": "Time-Series LSTM",
                "artifact_path": "ml/price_forecasting/model/crop_price_lstm.keras",
                "latency_ms": None
            }

        # 3. Yield Forecasting Subsystem
        try:
            t0 = time.time()
            from ml.yield_forecasting.model.predict import load_yield_inference_artifacts
            self.artifacts["yield_forecasting"] = load_yield_inference_artifacts()
            latency = round((time.time() - t0) * 1000.0, 2)
            self.status["yield_forecasting"] = {
                "status": "loaded",
                "model_type": "Deep Neural Network Regressor",
                "artifact_path": "ml/yield_forecasting/model/crop_yield_dnn.keras",
                "latency_ms": latency
            }
            logger.info(f"Loaded Yield Forecasting DNN in {latency}ms")
        except Exception as e:
            logger.error(f"Failed to load Yield Forecasting model: {e}", exc_info=True)
            self.status["yield_forecasting"] = {
                "status": f"failed: {str(e)}",
                "model_type": "Deep Neural Network Regressor",
                "artifact_path": "ml/yield_forecasting/model/crop_yield_dnn.keras",
                "latency_ms": None
            }

    def get_status(self) -> Dict[str, Any]:
        """
        Returns the operational status of all ML models.
        """
        return {
            "crop_recommendation": self.status["crop_recommendation"]["status"],
            "price_forecasting": self.status["price_forecasting"]["status"],
            "yield_forecasting": self.status["yield_forecasting"]["status"],
            "details": self.status
        }


# Global singleton instance
model_manager = ModelManager()
