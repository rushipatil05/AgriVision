import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from ml.price_forecasting.config import (
    RAW_DATA_PATH,
    EDA_OUTPUT_DIR,
    COL_DATE,
    COL_COMMODITY,
    COL_MARKET,
    COL_MODAL_PRICE
)


def generate_price_eda(file_path=RAW_DATA_PATH, output_dir=EDA_OUTPUT_DIR):
    """
    Generates exploratory data analysis (EDA) charts for Commodity Price Forecasting:
    1. Historical price trends for top commodities over time.
    2. Commodity frequency distribution in the mandi records.
    3. Market (mandi) volume distribution.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(file_path)
    df["date"] = pd.to_datetime(df[COL_DATE], format="%d/%m/%Y", errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")
    
    sns.set_theme(style="whitegrid")
    
    # 1. Price Trends for Top Commodities
    plt.figure(figsize=(14, 6))
    top_commodities = df[COL_COMMODITY].value_counts().head(5).index.tolist()
    sub_df = df[df[COL_COMMODITY].isin(top_commodities)].copy()
    
    # Resample monthly median price for clear visual trend lines (use ME for pandas 3.0+)
    monthly_prices = sub_df.groupby([pd.Grouper(key="date", freq="ME"), COL_COMMODITY])[COL_MODAL_PRICE].median().reset_index()
    
    sns.lineplot(data=monthly_prices, x="date", y=COL_MODAL_PRICE, hue=COL_COMMODITY, marker="o", linewidth=2)
    plt.title("Commodity Price Forecasting: Historical Modal Price Trends (Monthly Median)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Timeline (Year)", fontsize=12)
    plt.ylabel("Modal Price (₹ / Quintal)", fontsize=12)
    plt.legend(title="Commodity", loc="upper left")
    plt.tight_layout()
    trend_plot_path = output_dir / "price_trends.png"
    plt.savefig(trend_plot_path, dpi=200)
    plt.close()
    print(f"Saved: {trend_plot_path.name}")
    
    # 2. Top Commodities Frequency Distribution
    plt.figure(figsize=(10, 5))
    comm_counts = df[COL_COMMODITY].value_counts().head(10)
    sns.barplot(x=comm_counts.values, y=comm_counts.index, hue=comm_counts.index, palette="mako", legend=False)
    plt.title("Commodity Distribution (Top 10 Mandi Traded Commodities)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Number of Recorded Observations", fontsize=12)
    plt.ylabel("Commodity", fontsize=12)
    plt.tight_layout()
    comm_plot_path = output_dir / "commodity_distribution.png"
    plt.savefig(comm_plot_path, dpi=200)
    plt.close()
    print(f"Saved: {comm_plot_path.name}")
    
    # 3. Market (Mandi) Distribution
    plt.figure(figsize=(10, 5))
    mkt_counts = df[COL_MARKET].value_counts().head(10)
    sns.barplot(x=mkt_counts.values, y=mkt_counts.index, hue=mkt_counts.index, palette="rocket", legend=False)
    plt.title("Market Distribution (Top 10 Mandis by Volume of Records)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Number of Records", fontsize=12)
    plt.ylabel("Market (Mandi)", fontsize=12)
    plt.tight_layout()
    mkt_plot_path = output_dir / "market_distribution.png"
    plt.savefig(mkt_plot_path, dpi=200)
    plt.close()
    print(f"Saved: {mkt_plot_path.name}")
    
    print("Price Forecasting EDA plots generated successfully.\n")


if __name__ == "__main__":
    generate_price_eda()
