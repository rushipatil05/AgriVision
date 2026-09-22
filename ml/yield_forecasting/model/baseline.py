import numpy as np
from typing import Dict, Any
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from ml.yield_forecasting.model.model_utils import compute_regression_metrics


class MedianYieldRegressor:
    """
    Baseline Regressor: Predicts the global median yield of the training partition.
    """
    def __init__(self):
        self.name = "Median Yield Baseline"
        self.median_val = 0.0

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.median_val = float(np.median(y))
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.full(shape=(X.shape[0],), fill_value=self.median_val)


class LinearYieldRegressor:
    """
    Ordinary Least Squares (Ridge Regularized) Regression Baseline.
    """
    def __init__(self, alpha: float = 1.0):
        self.name = "Ridge Linear Regression"
        self.model = Ridge(alpha=alpha, random_state=42)

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.model.fit(X, y.ravel())
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        preds = self.model.predict(X)
        return np.maximum(0.0, preds)


class RandomForestYieldRegressor:
    """
    Random Forest Regression Baseline for non-linear feature interaction.
    """
    def __init__(self, n_estimators: int = 100, max_depth: int = 18, random_state: int = 42):
        self.name = "Random Forest Regressor"
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            n_jobs=-1,
            random_state=random_state
        )

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.model.fit(X, y.ravel())
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        preds = self.model.predict(X)
        return np.maximum(0.0, preds)


class GradientBoostingYieldRegressor:
    """
    Histogram-based Gradient Boosting Regressor (LightGBM-style algorithm)
    optimized for large multi-category tabular feature representations.
    """
    def __init__(self, max_iter: int = 150, learning_rate: float = 0.08, max_depth: int = 12, random_state: int = 42):
        self.name = "Histogram Gradient Boosting"
        self.model = HistGradientBoostingRegressor(
            max_iter=max_iter,
            learning_rate=learning_rate,
            max_depth=max_depth,
            random_state=random_state
        )

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.model.fit(X, y.ravel())
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        preds = self.model.predict(X)
        return np.maximum(0.0, preds)
