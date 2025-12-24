import pandas as pd
import numpy as np
from pathlib import Path

def _season_from_month(m: int) -> str:
    # India-friendly seasons (approx)
    if m in [3, 4, 5]:
        return "Summer"
    if m in [6, 7, 8, 9]:
        return "Monsoon"
    return "Winter"

def _festival_for_date(dt: pd.Timestamp) -> str:
    # Approx festival windows (synthetic but realistic)
    m, d = dt.month, dt.day
    # New Year
    if (m == 12 and d >= 26) or (m == 1 and d <= 3):
        return "NewYear"
    # Pongal / Makar Sankranti (mid-Jan)
    if m == 1 and 12 <= d <= 17:
        return "Pongal_Sankranti"
    # Ramzan/Eid varies; approximate in Apr/May
    if m in [4, 5] and 5 <= d <= 15:
        return "Eid_Season"
    # Back to School (Jun/Jul)
    if m in [6, 7] and 1 <= d <= 20:
        return "BackToSchool"
    # Independence Day (Aug mid)
    if m == 8 and 10 <= d <= 16:
        return "IndependenceWeek"
    # Diwali season (Oct/Nov)
    if (m == 10 and d >= 15) or (m == 11 and d <= 15):
        return "Diwali"
    # Christmas
    if m == 12 and 18 <= d <= 25:
        return "Christmas"
    return "None"

def generate_general_store_dataset(
    start_date="2020-01-01",
    end_date="2024-12-31",
    seed=42
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range(start=start_date, end=end_date, freq="D")

    # --- Catalog (department -> subcategory -> items) ---
    catalog = {
        "Food": {
            "Staples": ["Rice", "Wheat Flour", "Pulses", "Cooking Oil", "Sugar", "Salt", "Spices"],
            "Snacks": ["Biscuits", "Chips", "Namkeen", "Chocolate"],
            "Beverages": ["Tea", "Coffee", "Soft Drinks", "Juice"],
            "Dairy": ["Milk", "Curd", "Butter", "Paneer"],
        },
        "Kitchen & Cooking": {
            "Cookware": ["Non-stick Pan", "Pressure Cooker", "Tawa", "Kadai"],
            "Appliances Small": ["Mixer Grinder", "Electric Kettle", "Toaster"],
            "Consumables": ["Gas Lighter", "Aluminium Foil", "Cling Wrap"],
        },
        "Utensils": {
            "Steel": ["Steel Plates", "Steel Bowls", "Steel Glasses"],
            "Plastic": ["Storage Boxes", "Water Bottles"],
            "Tools": ["Knife Set", "Peeler", "Ladle Set"],
        },
        "Clothing": {
            "Basics": ["T-Shirts", "Jeans", "Socks", "Innerwear"],
            "Seasonal": ["Raincoat", "Sweater", "Jacket"],
            "Ethnic": ["Kurta", "Saree"],
        },
        "Small Electronics": {
            "Accessories": ["Earphones", "Charger", "USB Cable", "Power Bank"],
            "Home": ["Extension Board", "LED Bulb", "Torch"],
            "Gadgets": ["Smart Watch Budget", "Bluetooth Speaker"],
        },
        "Books": {
            "Academic": ["School Notebook Pack", "Exam Guide", "Textbook"],
            "General": ["Novel", "Comics"],
        },
        "Stationery": {
            "School": ["Pens", "Pencils", "Eraser", "Geometry Box"],
            "Office": ["Stapler", "A4 Paper", "Marker"],
        },
        "Home Essentials": {
            "Cleaning": ["Detergent", "Dish Wash", "Floor Cleaner", "Toilet Cleaner"],
            "Personal Care": ["Soap", "Shampoo", "Toothpaste", "Sanitary Pads"],
        }
    }

    # Base prices & margins by department (realistic ranges)
    dept_price_range = {
        "Food": (20, 350),
        "Kitchen & Cooking": (80, 2500),
        "Utensils": (60, 1200),
        "Clothing": (150, 1800),
        "Small Electronics": (120, 3000),
        "Books": (80, 900),
        "Stationery": (10, 300),
        "Home Essentials": (20, 600),
    }
    dept_margin = {
        "Food": 0.18,
        "Kitchen & Cooking": 0.22,
        "Utensils": 0.20,
        "Clothing": 0.35,
        "Small Electronics": 0.25,
        "Books": 0.15,
        "Stationery": 0.28,
        "Home Essentials": 0.24,
    }

    # Demand multipliers by festival (what sells more)
    festival_lift = {
        "None": {},
        "NewYear": {"Food": 1.08, "Small Electronics": 1.12},
        "Pongal_Sankranti": {"Food": 1.18, "Utensils": 1.10, "Kitchen & Cooking": 1.12},
        "Eid_Season": {"Food": 1.15, "Clothing": 1.20},
        "BackToSchool": {"Stationery": 1.35, "Books": 1.28},
        "IndependenceWeek": {"Food": 1.06},
        "Diwali": {"Food": 1.25, "Utensils": 1.18, "Kitchen & Cooking": 1.20, "Small Electronics": 1.22, "Clothing": 1.18},
        "Christmas": {"Food": 1.12, "Books": 1.08, "Small Electronics": 1.14},
    }

    # Seasonal lifts (approx)
    season_lift = {
        "Summer": {"Beverages": 1.25, "Dairy": 1.05, "LED Bulb": 0.95},
        "Monsoon": {"Raincoat": 1.35, "Floor Cleaner": 1.05},
        "Winter": {"Sweater": 1.40, "Jacket": 1.25, "Tea": 1.12},
    }

    rows = []
    # Store-level growth across years (like business growth)
    # 8% per year -> daily factor
    yearly_growth = 0.08
    daily_growth = (1 + yearly_growth) ** (1 / 365) - 1

    for i, dt in enumerate(dates):
        dow = dt.dayofweek
        is_weekend = int(dow >= 5)
        season = _season_from_month(dt.month)
        fest = _festival_for_date(dt)

        # General footfall factor: weekends higher, month start salary effect
        month_start = int(dt.day <= 5)
        month_end = int(dt.day >= 25)
        footfall = 1.0
        footfall *= (1.10 if is_weekend else 1.00)
        footfall *= (1.06 if month_start else 1.00)
        footfall *= (0.98 if month_end else 1.00)

        # Long-term growth
        growth = (1.0 + daily_growth) ** i

        # Random shock days (stockouts/powercut/promo blast)
        shock = 1.0
        if rng.random() < 0.007:   # ~0.7% of days: stockout-like dip
            shock *= rng.uniform(0.70, 0.88)
        if rng.random() < 0.010:   # ~1% of days: special promotion day spike
            shock *= rng.uniform(1.08, 1.22)

        for dept, subcats in catalog.items():
            # Dept baseline demand (units scale)
            dept_base = {
                "Food": 220,
                "Home Essentials": 90,
                "Stationery": 70,
                "Books": 35,
                "Clothing": 55,
                "Utensils": 40,
                "Kitchen & Cooking": 28,
                "Small Electronics": 30,
            }[dept]

            # Festival lift by dept
            dept_fest_lift = festival_lift.get(fest, {}).get(dept, 1.0)

            for subcat, items in subcats.items():
                # Subcategory base modifier
                subcat_mod = 1.0
                if dept == "Food" and subcat == "Beverages" and season == "Summer":
                    subcat_mod *= 1.25
                if dept == "Clothing" and subcat == "Seasonal":
                    subcat_mod *= 1.15
                if dept == "Books" and fest == "BackToSchool":
                    subcat_mod *= 1.30
                if dept == "Stationery" and fest == "BackToSchool":
                    subcat_mod *= 1.40

                for item in items:
                    # Item-specific seasonal lifts
                    item_lift = 1.0
                    item_lift *= season_lift.get(season, {}).get(item, 1.0)
                    item_lift *= season_lift.get(season, {}).get(subcat, 1.0)

                    # Price & discount
                    pmin, pmax = dept_price_range[dept]
                    base_price = rng.uniform(pmin, pmax)

                    # Discount strategy: more discount on clothing & electronics during big festivals
                    discount_pct = 0.0
                    promo_type = "None"
                    if fest in ["Diwali", "NewYear", "Christmas"] and dept in ["Clothing", "Small Electronics", "Kitchen & Cooking"]:
                        discount_pct = rng.choice([0, 5, 10, 15, 20], p=[0.15, 0.20, 0.30, 0.25, 0.10])
                        promo_type = rng.choice(["Flat", "Combo", "BOGO"], p=[0.6, 0.25, 0.15])
                    elif dept in ["Food", "Home Essentials"] and rng.random() < 0.08:
                        discount_pct = rng.choice([0, 3, 5, 8, 10], p=[0.20, 0.25, 0.30, 0.15, 0.10])
                        promo_type = rng.choice(["Flat", "Combo"], p=[0.8, 0.2])
                    else:
                        if rng.random() < 0.03:
                            discount_pct = rng.choice([0, 5, 10], p=[0.5, 0.35, 0.15])
                            promo_type = "Flat"

                    sell_price = base_price * (1 - discount_pct / 100.0)

                    # Demand model (units): baseline * effects * randomness
                    # Keep units realistic: cheap items sell more, expensive sell less
                    affordability = 1.0
                    if sell_price > 1500:
                        affordability = 0.35
                    elif sell_price > 700:
                        affordability = 0.55
                    elif sell_price > 300:
                        affordability = 0.75

                    mean_units = (
                        dept_base
                        * 0.015  # scaling per item
                        * footfall
                        * growth
                        * shock
                        * dept_fest_lift
                        * subcat_mod
                        * item_lift
                        * affordability
                    )

                    # Make units follow a Poisson-like randomness but stable
                    units = int(rng.poisson(lam=max(mean_units, 0.05)))

                    # Ensure some items sell occasionally even if low
                    if units == 0 and rng.random() < 0.06:
                        units = 1

                    # Cost & profit
                    margin = dept_margin[dept]
                    cost_per_unit = sell_price * (1 - margin)
                    revenue = units * sell_price
                    cost = units * cost_per_unit
                    profit = revenue - cost

                    rows.append({
                        "date": dt.date(),
                        "department": dept,
                        "subcategory": subcat,
                        "item_name": item,
                        "units_sold": units,
                        "unit_price": round(base_price, 2),
                        "discount_pct": float(discount_pct),
                        "sell_price": round(sell_price, 2),
                        "revenue": round(revenue, 2),
                        "cost": round(cost, 2),
                        "profit": round(profit, 2),
                        "season": season,
                        "festival": fest,
                        "promo_type": promo_type,
                        "day_of_week": int(dow),
                        "is_weekend": is_weekend,
                        "is_month_start": int(dt.day <= 5),
                        "is_month_end": int(dt.day >= 25),
                    })

    df = pd.DataFrame(rows)

    # Optional: remove tiny noise rows where nothing sold
    # but keep some zeros for realism
    return df


def save_dataset(df: pd.DataFrame, path="data/general_store_sales_5y.csv"):
    Path("data").mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"✅ Saved: {path} | rows={len(df):,} | cols={df.shape[1]}")


if __name__ == "__main__":
    df = generate_general_store_dataset()
    save_dataset(df)
    print(df.head())
    print(df.tail())
