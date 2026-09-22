import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from typing import Tuple
import tensorflow as tf
from tensorflow.keras import layers, models, regularizers


def build_price_lstm_model(
    input_shape: Tuple[int, int] = (30, 1),
    lstm_units: int = 64,
    dense_units: int = 32,
    dropout_rate: float = 0.2,
    learning_rate: float = 0.001
) -> tf.keras.Model:
    """
    Builds and compiles the Time-Series LSTM Neural Network for Crop Market Price Forecasting.
    
    Architectural Specification:
    ----------------------------
    Input Layer: Shape (sequence_length=30, features=1)
      ↓
    LSTM Layer: 64 recurrent units, return_sequences=False, L2 regularization (1e-4)
      ↓
    Dropout Layer: 0.2 (Regularization against temporal overfitting)
      ↓
    Dense Layer: 32 units with ReLU activation and L2 kernel regularization
      ↓
    Dropout Layer: 0.2
      ↓
    Dense Output Layer: 1 unit with Linear activation (Forecasted continuous price)
    
    Loss Function: Mean Squared Error (MSE)
    Optimizer: Adam (learning_rate=0.001)
    """
    model = models.Sequential([
        layers.Input(shape=input_shape, name="price_sequence_input"),
        layers.LSTM(
            units=lstm_units,
            return_sequences=False,
            kernel_regularizer=regularizers.l2(1e-4),
            name="lstm_temporal_encoder"
        ),
        layers.Dropout(rate=dropout_rate, name="dropout_lstm"),
        layers.Dense(
            units=dense_units,
            activation="relu",
            kernel_regularizer=regularizers.l2(1e-4),
            name="dense_projection"
        ),
        layers.Dropout(rate=dropout_rate, name="dropout_dense"),
        layers.Dense(
            units=1,
            activation="linear",
            name="price_forecast_output"
        )
    ], name="AgriPulse_PriceForecasting_LSTM")
    
    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss="mean_squared_error",
        metrics=["mean_absolute_error"]
    )
    return model
