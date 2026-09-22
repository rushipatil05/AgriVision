import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from ml.yield_forecasting.config import (
    RAW_DATA_PATH,
    EDA_OUTPUT_DIR,
    COL_STATE,
    COL_YEAR,
    COL_CROP,
    COL_AREA,
    COL_PRODUCTION,
    COL_YIELD,
    BENCHMARK_CROPS
)


def generate_yield_eda(file_path=RAW_DATA_PATH, output_dir=EDA_OUTPUT_DIR):
    """
    Generates exploratory data analysis (EDA) charts for Crop Yield Forecasting:
    1. Historical yield trends over years for major staple crops.
    2. Crop frequency and total production distribution.
    3. State-wise total agricultural production volume distribution.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(file_path)
    
    # Clean and compute yield
    valid = (df[COL_AREA] > 0) & (df[COL_PRODUCTION].notnull())
    df = df[valid].copy()
    df[COL_YIELD] = df[COL_PRODUCTION] / df[COL_AREA]
    
    sns.set_theme(style="whitegrid")
    
    # 1. Historical Yield Trend over Years for Major Crops
    plt.figure(figsize=(14, 6))
    sub_df = df[df[COL_CROP].isin(["Rice", "Wheat", "Maize", "Groundnut", "Bajra"])].copy()
    yearly_yield = sub_df.groupby([COL_YEAR, COL_CROP])[COL_YIELD].median().reset_index()
    
    sns.lineplot(data=yearly_yield, x=COL_YEAR, y=COL_YIELD, hue=COL_CROP, marker="o", linewidth=2)
    plt.title("Crop Yield Forecasting: Historical Yield Trends Over Time (Median Tonnes / Hectare)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Crop Year", fontsize=12)
    plt.ylabel("Yield (Tonnes / Hectare)", fontsize=12)
    plt.legend(title="Crop", loc="upper left")
    plt.tight_layout()
    trend_plot_path = output_dir / "yield_trends_over_years.png"
    plt.savefig(trend_plot_path, dpi=200)
    plt.close()
    print(f"Saved: {trend_plot_path.name}")
    
    # 2. Top Crops by Record Frequency
    plt.figure(figsize=(10, 5))
    top_crops = df[COL_CROP].value_counts().head(10)
    sns.barplot(x=top_crops.values, y=top_crops.index, hue=top_crops.index, palette="crest", legend=False)
    plt.title("Crop Distribution (Top 10 Most Cultivated / Recorded Crops)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Number of District-Season Records", fontsize=12)
    plt.ylabel("Crop", fontsize=12)
    plt.tight_layout()
    crop_plot_path = output_dir / "crop_distribution.png"
    plt.savefig(crop_plot_path, dpi=200)
    plt.close()
    print(f"Saved: {crop_plot_path.name}")
    
    # 3. State-wise Record Volume
    plt.figure(figsize=(10, 6))
    state_counts = df[COL_STATE].value_counts().head(10)
    sns.barplot(x=state_counts.values, y=state_counts.index, hue=state_counts.index, palette="flare", legend=False)
    plt.title("State Distribution (Top 10 States by Agricultural Survey Count)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Number of Records", fontsize=12)
    plt.ylabel("State", fontsize=12)
    plt.tight_layout()
    state_plot_path = output_dir / "state_distribution.png"
    plt.savefig(state_plot_path, dpi=200)
    plt.close()
    print(f"Saved: {state_plot_path.name}")
    
    print("Crop Yield EDA plots generated successfully.\n")


if __name__ == "__main__":
    generate_yield_eda()
