import os
import random
import json
from pathlib import Path
from typing import Tuple, Dict, Any, List
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)
import tensorflow as tf


def set_seed(seed: int = 42) -> None:
    """
    Ensures strict determinism across Python, NumPy, and TensorFlow.
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)


def reshape_tabular_to_sequence(X: np.ndarray) -> np.ndarray:
    """
    Reshapes tabular 2D array (samples, 7) into 3D sequence array (samples, timesteps=7, features=1)
    for consumption by LSTM neural networks.
    
    Technical Context:
    The crop recommendation dataset consists of 7 agronomic features. Because the project proposal
    specifies an LSTM architecture, each sample is structured as a 1D sequence of 7 ordered feature
    tokens [N, P, K, Temperature, Humidity, pH, Rainfall].
    """
    if X.ndim == 2:
        return X.reshape((X.shape[0], X.shape[1], 1))
    elif X.ndim == 1:
        return X.reshape((1, len(X), 1))
    return X


def calculate_top_k_accuracy(y_true: np.ndarray, y_prob: np.ndarray, k: int = 5) -> float:
    """
    Calculates top-k classification accuracy:
    Returns the proportion of samples where true label is within top-k highest probability predictions.
    """
    top_k_preds = np.argsort(y_prob, axis=1)[:, -k:]
    correct = 0
    for true_label, top_k in zip(y_true, top_k_preds):
        if true_label in top_k:
            correct += 1
    return float(correct / len(y_true))


def compute_comprehensive_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: np.ndarray,
    target_names: List[str]
) -> Dict[str, Any]:
    """
    Calculates all classification metrics: Accuracy, Precision, Recall, F1 (macro & weighted),
    Top-1, Top-3, and Top-5 accuracy.
    """
    acc = float(accuracy_score(y_true, y_pred))
    p_macro = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
    r_macro = float(recall_score(y_true, y_pred, average="macro", zero_division=0))
    f1_macro = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    
    p_weighted = float(precision_score(y_true, y_pred, average="weighted", zero_division=0))
    r_weighted = float(recall_score(y_true, y_pred, average="weighted", zero_division=0))
    f1_weighted = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))
    
    top_1 = calculate_top_k_accuracy(y_true, y_prob, k=1)
    top_3 = calculate_top_k_accuracy(y_true, y_prob, k=3)
    top_5 = calculate_top_k_accuracy(y_true, y_prob, k=5)
    
    cls_report = classification_report(y_true, y_pred, target_names=target_names, output_dict=True, zero_division=0)
    
    return {
        "accuracy": round(acc, 4),
        "precision_macro": round(p_macro, 4),
        "recall_macro": round(r_macro, 4),
        "f1_macro": round(f1_macro, 4),
        "precision_weighted": round(p_weighted, 4),
        "recall_weighted": round(r_weighted, 4),
        "f1_weighted": round(f1_weighted, 4),
        "top_1_accuracy": round(top_1, 4),
        "top_3_accuracy": round(top_3, 4),
        "top_5_accuracy": round(top_5, 4),
        "classification_report": cls_report
    }


def plot_and_save_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: List[str],
    title: str,
    output_path: Path
) -> None:
    """
    Renders a clear 22x22 confusion matrix with crop names as tick labels.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(14, 12))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
        cbar=True,
        square=True
    )
    plt.title(title, fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Predicted Crop Class", fontsize=12, labelpad=10)
    plt.ylabel("True Crop Class", fontsize=12, labelpad=10)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Confusion Matrix saved to: {output_path.name}")
