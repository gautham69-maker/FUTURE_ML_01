import pandas as pd
import numpy as np
from pathlib import Path

def generate_retail_sales_data(
    start_date="2023-01-01",
    end_date="2024-12-31",
    base_sales=1200,
    trend_per_day=0.5,
    noise_level=150,
    seed=42
):
    np.random.seed(seed)

    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    n = len(dates)

    # Trend
    trend = base_sales + trend_per_day * np.arange(n)

    # Weekly seasonality (weekends higher)
    weekly = 200 * np.sin(2 * np.pi * dates.dayofweek / 7)

    # Yearly seasonality (festive effect)
    yearly = 300 * np.sin(2 * np.pi * dates.dayofyear / 365)

    # Random noise
    noise = np.random.normal(0, noise_level, n)

    sales = trend + weekly + yearly + noise
    sales = np.maximum(sales, 0).round(2)

    df = pd.DataFrame({
        "date": dates,
        "sales": sales
    })

    return df


def save_dataset(df, path="data/retail_sales.csv"):
    Path("data").mkdir(exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Dataset saved to {path}")


def load_dataset(path="data/retail_sales.csv"):
    df = pd.read_csv(path, parse_dates=["date"])
    return df


if __name__ == "__main__":
    df = generate_retail_sales_data()
    save_dataset(df)
    print(df.head())
