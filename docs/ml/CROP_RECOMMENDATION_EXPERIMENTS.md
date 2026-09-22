# AgriPulse ML Experiment Log: Crop Recommendation

This document records all baseline and deep learning training iterations conducted on the Crop Recommendation module.

---

## Experiment History

### Experiment EXP-CR-001: Logistic Regression Baseline
- **Date**: 2026-08-28
- **Model**: Multinomial Logistic Regression (`solver='lbfgs'`, `max_iter=1500`)
- **Data Partitions**: Train: 1,540 | Val: 330 | Test: 330
- **Feature Scaling**: StandardScaler (fitted strictly on Train)
- **Validation Accuracy**: `0.9667`
- **Validation F1 (Macro)**: `0.9665`
- **Test Accuracy**: `0.9788`
- **Test F1 (Macro)**: `0.9787`
- **Top-3 Accuracy**: `1.0000`
- **Top-5 Accuracy**: `1.0000`
- **Notes**: Serves as linear decision boundary reference. Demonstrates strong baseline separability across soil and climatic clusters.

---

### Experiment EXP-CR-002: Random Forest Classifier Baseline
- **Date**: 2026-08-28
- **Model**: Random Forest Classifier (`n_estimators=100`, `max_depth=12`, `random_state=42`)
- **Data Partitions**: Train: 1,540 | Val: 330 | Test: 330
- **Feature Scaling**: StandardScaler (fitted strictly on Train)
- **Validation Accuracy**: `0.9909`
- **Validation F1 (Macro)**: `0.9909`
- **Test Accuracy**: `0.9939`
- **Test F1 (Macro)**: `0.9939`
- **Top-3 Accuracy**: `1.0000`
- **Top-5 Accuracy**: `1.0000`
- **Notes**: Tree ensemble baseline capturing non-linear soil-crop interaction thresholds. Highest test F1-macro score among all evaluated architectures.

---

### Experiment EXP-CR-003: LSTM Recurrent Neural Network (Primary Proposal Architecture)
- **Date**: 2026-08-28
- **Model**: LSTM Neural Network (`Input(7, 1)` $\rightarrow$ `LSTM(64)` $\rightarrow$ `Dropout(0.2)` $\rightarrow$ `Dense(64, relu)` $\rightarrow$ `Dropout(0.2)` $\rightarrow$ `Dense(22, softmax)`)
- **Hyperparameters**: `optimizer='Adam'`, `learning_rate=0.001`, `batch_size=32`, `loss='sparse_categorical_crossentropy'`
- **Regularization**: `EarlyStopping(patience=20)`, `ReduceLROnPlateau(patience=7, factor=0.5)`
- **Epochs Trained**: 96 (Early stopping triggered, best weights at epoch 76)
- **Training Time**: 32.38 seconds (CPU)
- **Validation Accuracy**: `0.9879`
- **Validation F1 (Macro)**: `0.9880`
- **Test Accuracy**: `0.9848`
- **Test F1 (Macro)**: `0.9848`
- **Top-3 Accuracy**: `1.0000`
- **Top-5 Accuracy**: `1.0000`
- **Notes**: Proposal-compliant deep learning network. Achieved 98.48% test accuracy and 100% Top-3 / Top-5 recommendation accuracy. Artifact serialized as primary production model.
