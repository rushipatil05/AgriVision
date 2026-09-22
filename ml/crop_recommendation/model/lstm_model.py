from typing import Tuple
import tensorflow as tf
from tensorflow.keras import layers, models, regularizers


def build_crop_lstm_model(
    input_shape: Tuple[int, int] = (7, 1),
    num_classes: int = 22,
    lstm_units: int = 64,
    dense_units: int = 64,
    dropout_rate: float = 0.2,
    learning_rate: float = 0.001
) -> tf.keras.Model:
    """
    Builds and compiles the LSTM Neural Network for Crop Recommendation.
    
    Architectural Specification:
    ----------------------------
    Input Layer: Shape (timesteps=7, features=1)
      ↓
    LSTM Layer: 64 recurrent memory units, return_sequences=False
      ↓
    Dropout Layer: 0.2 (Prevents co-adaptation / overfitting)
      ↓
    Dense Layer: 64 hidden units with ReLU activation and L2 kernel regularization
      ↓
    Dropout Layer: 0.2
      ↓
    Output Layer: 22 units with Softmax activation (Multiclass probability distribution)
    
    Loss Function: Sparse Categorical Crossentropy
    Optimizer: Adam (learning_rate=0.001)
    """
    model = models.Sequential([
        layers.Input(shape=input_shape, name="agronomic_feature_sequence_input"),
        layers.LSTM(
            units=lstm_units,
            return_sequences=False,
            kernel_regularizer=regularizers.l2(1e-4),
            name="lstm_feature_encoder"
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
            units=num_classes,
            activation="softmax",
            name="crop_recommendation_output"
        )
    ], name="AgriPulse_CropRecommendation_LSTM")
    
    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model
