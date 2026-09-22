import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import tensorflow as tf
from tensorflow.keras import layers, models, regularizers


def build_yield_deep_model(
    input_dim: int,
    dense_units_1: int = 128,
    dense_units_2: int = 64,
    dense_units_3: int = 32,
    dropout_rate: float = 0.2,
    learning_rate: float = 0.001
) -> tf.keras.Model:
    """
    Constructs and compiles the Deep Neural Network Regressor for Crop Yield Forecasting.
    
    Architectural Specification:
    ----------------------------
    Input Layer: Shape (input_dim,)
      ↓
    Dense Layer: 128 units, ReLU activation, L2 kernel regularization (1e-4)
      ↓
    Dropout Layer: 0.20 (Regularization against category co-adaptation)
      ↓
    Dense Layer: 64 units, ReLU activation, L2 kernel regularization (1e-4)
      ↓
    Dropout Layer: 0.20
      ↓
    Dense Layer: 32 units, ReLU activation, L2 kernel regularization (1e-4)
      ↓
    Dense Output Layer: 1 unit, Linear activation (Predicted Yield in Tonnes/Hectare)
    
    Loss Function: Mean Squared Error (MSE)
    Optimizer: Adam (learning_rate=0.001)
    """
    model = models.Sequential([
        layers.Input(shape=(input_dim,), name="crop_yield_features_input"),
        layers.Dense(
            units=dense_units_1,
            activation="relu",
            kernel_regularizer=regularizers.l2(1e-4),
            name="dense_layer_1"
        ),
        layers.Dropout(rate=dropout_rate, name="dropout_1"),
        layers.Dense(
            units=dense_units_2,
            activation="relu",
            kernel_regularizer=regularizers.l2(1e-4),
            name="dense_layer_2"
        ),
        layers.Dropout(rate=dropout_rate, name="dropout_2"),
        layers.Dense(
            units=dense_units_3,
            activation="relu",
            kernel_regularizer=regularizers.l2(1e-4),
            name="dense_layer_3"
        ),
        layers.Dense(
            units=1,
            activation="linear",
            name="yield_forecast_output"
        )
    ], name="AgriPulse_YieldForecasting_DNN")
    
    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss="mean_squared_error",
        metrics=["mean_absolute_error"]
    )
    return model
