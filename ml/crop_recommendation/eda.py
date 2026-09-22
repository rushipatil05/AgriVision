import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server generation
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from ml.crop_recommendation.config import (
    RAW_DATA_PATH,
    EDA_OUTPUT_DIR,
    FEATURE_COLUMNS,
    TARGET_COLUMN
)


def generate_crop_eda(file_path=RAW_DATA_PATH, output_dir=EDA_OUTPUT_DIR):
    """
    Generates exploratory data analysis (EDA) charts for Crop Recommendation:
    1. Class distribution bar plot
    2. Feature distributions (histograms with KDE)
    3. Feature correlation matrix heatmap
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(file_path)
    
    # Set aesthetics
    sns.set_theme(style="whitegrid")
    
    # 1. Class Distribution Plot
    plt.figure(figsize=(14, 6))
    class_counts = df[TARGET_COLUMN].value_counts()
    ax = sns.barplot(x=class_counts.index, y=class_counts.values, hue=class_counts.index, palette="viridis", legend=False)
    plt.title("Crop Recommendation: Class Frequency Distribution", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Crop Type", fontsize=12)
    plt.ylabel("Number of Samples", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    class_plot_path = output_dir / "crop_class_distribution.png"
    plt.savefig(class_plot_path, dpi=200)
    plt.close()
    print(f"Saved: {class_plot_path.name}")
    
    # 2. Feature Distributions Subplots
    fig, axes = plt.subplots(3, 3, figsize=(15, 12))
    axes = axes.flatten()
    
    for i, col in enumerate(FEATURE_COLUMNS):
        sns.histplot(df[col], kde=True, ax=axes[i], color="#10b981", bins=25)
        axes[i].set_title(f"Distribution of {col}", fontsize=11, fontweight="bold")
        axes[i].set_xlabel(col, fontsize=10)
        axes[i].set_ylabel("Frequency", fontsize=10)
        
    # Remove unused subplots
    for j in range(len(FEATURE_COLUMNS), len(axes)):
        fig.delaxes(axes[j])
        
    plt.suptitle("Crop Recommendation: Agronomic Feature Distributions", fontsize=14, fontweight="bold", y=0.98)
    plt.tight_layout()
    dist_plot_path = output_dir / "feature_distributions.png"
    plt.savefig(dist_plot_path, dpi=200)
    plt.close()
    print(f"Saved: {dist_plot_path.name}")
    
    # 3. Feature Correlation Matrix Heatmap
    plt.figure(figsize=(9, 7))
    corr = df[FEATURE_COLUMNS].corr()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, square=True, linewidths=0.5)
    plt.title("Crop Recommendation: Feature Correlation Matrix", fontsize=14, fontweight="bold", pad=15)
    plt.tight_layout()
    corr_plot_path = output_dir / "correlation_matrix.png"
    plt.savefig(corr_plot_path, dpi=200)
    plt.close()
    print(f"Saved: {corr_plot_path.name}")
    
    print("Crop Recommendation EDA plots generated successfully.\n")


if __name__ == "__main__":
    generate_crop_eda()
