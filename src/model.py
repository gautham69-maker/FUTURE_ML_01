import pandas as pd
from prophet import Prophet
from pathlib import Path


DATA_PATH = "outputs/daily_total_revenue.csv"


def load_time_series(path: str = DATA_PATH) -> pd.DataFrame:
    """
    Load aggregated daily revenue time series.
    Expected columns: ds (date), y (revenue)
    """
    df = pd.read_csv(path, parse_dates=["ds"])
    return df


def train_prophet_model(df: pd.DataFrame) -> Prophet:
    """
    Train Prophet model with sensible defaults for retail data.
    """
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode="multiplicative"
    )
    model.fit(df)
    return model


def generate_forecast(
    model: Prophet,
    history_df: pd.DataFrame,
    periods: int = 90
) -> pd.DataFrame:
    """
    Generate future forecast.
    """
    future = model.make_future_dataframe(periods=periods, freq="D")
    forecast = model.predict(future)

    return forecast[
        ["ds", "yhat", "yhat_lower", "yhat_upper"]
    ]


def save_forecast(df: pd.DataFrame, output_dir: str = "outputs"):
    Path(output_dir).mkdir(exist_ok=True)
    path = f"{output_dir}/forecast.csv"
    df.to_csv(path, index=False)
    print(f"✅ Forecast saved to {path}")


if __name__ == "__main__":
    df_ts = load_time_series()
    print("Loaded data:", df_ts.shape)

    model = train_prophet_model(df_ts)
    forecast_df = generate_forecast(model, df_ts, periods=90)

    save_forecast(forecast_df)

    print("\nForecast preview:")
    print(forecast_df.tail())
