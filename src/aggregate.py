import pandas as pd
from pathlib import Path


DATA_PATH = "data/general_store_sales_5y.csv"


def load_raw_data(path: str = DATA_PATH) -> pd.DataFrame:
    """
    Load item-level general store sales data.
    """
    df = pd.read_csv(path, parse_dates=["date"])
    return df


def aggregate_daily_total_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate item-level data to daily total revenue.
    Output format is Prophet-ready: columns ['ds', 'y']
    """
    daily = (
        df.groupby("date", as_index=False)["revenue"]
        .sum()
        .rename(columns={"date": "ds", "revenue": "y"})
        .sort_values("ds")
    )
    return daily


def aggregate_daily_by_department(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate daily revenue by department.
    Output columns: ds, department, y
    """
    dept_daily = (
        df.groupby(["date", "department"], as_index=False)["revenue"]
        .sum()
        .rename(columns={"date": "ds", "revenue": "y"})
        .sort_values("ds")
    )
    return dept_daily


def save_aggregates(
    daily_total: pd.DataFrame,
    daily_by_dept: pd.DataFrame,
    output_dir: str = "outputs"
):
    Path(output_dir).mkdir(exist_ok=True)

    daily_total.to_csv(f"{output_dir}/daily_total_revenue.csv", index=False)
    daily_by_dept.to_csv(f"{output_dir}/daily_revenue_by_department.csv", index=False)

    print("✅ Aggregated files saved:")
    print(" - outputs/daily_total_revenue.csv")
    print(" - outputs/daily_revenue_by_department.csv")


if __name__ == "__main__":
    df_raw = load_raw_data()

    daily_total = aggregate_daily_total_revenue(df_raw)
    daily_by_dept = aggregate_daily_by_department(df_raw)

    save_aggregates(daily_total, daily_by_dept)

    print("\nPreview (Daily Total):")
    print(daily_total.head())
