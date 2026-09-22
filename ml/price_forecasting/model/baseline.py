import numpy as np
from typing import Dict, Any
from sklearn.linear_model import LinearRegression
from ml.price_forecasting.model.model_utils import compute_forecast_metrics


class NaiveLastValueForecaster:
    """
    Naive Baseline: Predicts that the price at step t will be equal to the price at step t-1
    (the most recent observed value in the lookback sequence).
    """
    def __init__(self):
        self.name = "Naive (Last-Value)"

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        X: shape (samples, seq_length, 1) or (samples, seq_length)
        Returns: last step value of each sample sequence.
        """
        if X.ndim == 3:
            return X[:, -1, 0]
        elif X.ndim == 2:
            return X[:, -1]
        raise ValueError("Unexpected input dimensions for NaiveForecaster.")


class MovingAverageForecaster:
    """
    Moving Average Baseline: Predicts that the future price will be the mean
    of the most recent k historical days in the lookback window.
    """
    def __init__(self, window: int = 7):
        self.window = window
        self.name = f"Moving Average ({window}-Day)"

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        X: shape (samples, seq_length, 1) or (samples, seq_length)
        """
        if X.ndim == 3:
            return np.mean(X[:, -self.window:, 0], axis=1)
        elif X.ndim == 2:
            return np.mean(X[:, -self.window:], axis=1)
        raise ValueError("Unexpected input dimensions for MovingAverageForecaster.")


class LinearRegressionForecaster:
    """
    Statistical Linear Regression Baseline: Fits an ordinary least squares regression
    over the lookback window to project the next step value.
    """
    def __init__(self):
        self.name = "Linear Regression (Autoregressive)"
        self.model = LinearRegression()

    def fit(self, X: np.ndarray, y: np.ndarray):
        X_2d = X.reshape(X.shape[0], -1)
        y_flat = y.ravel()
        self.model.fit(X_2d, y_flat)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        X_2d = X.reshape(X.shape[0], -1)
        return self.model.predict(X_2d)
