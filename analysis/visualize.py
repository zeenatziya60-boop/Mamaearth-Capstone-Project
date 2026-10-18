
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "visualizations"
OUTPUT_DIR.mkdir(exist_ok=True)

# Load the latest cleaned dataset
df = pd.read_csv(DATA_DIR / "cleaned_mamaearth_data.csv")
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

# 1. Return rate by product category
category_returns = df.groupby("category").agg(
    total_orders=("order_id", "count"),
    returned_orders=("returned", "sum")
)

category_returns["return_rate_pct"] = (
    category_returns["returned_orders"]
    / category_returns["total_orders"] * 100
)

category_returns["return_rate_pct"].plot(
    kind="bar", figsize=(8, 5)
)
plt.title("Return Rate by Product Category")
plt.xlabel("Category")
plt.ylabel("Return Rate (%)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "return_rate_by_category.png",
    dpi=300
)
plt.close()

# 2. Monthly revenue excluding quantity outliers
df["month"] = df["order_date"].dt.to_period("M").astype(str)

valid = df[
    df["quantity_outlier"].astype(str).str.lower() != "true"
]

monthly = valid.groupby("month")["revenue"].sum()

monthly.plot(
    kind="line", marker="o", figsize=(9, 5)
)
plt.title("Monthly Revenue (Excluding Quantity Outliers)")
plt.xlabel("Month")
plt.ylabel("Known Revenue")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "monthly_revenue_outlier_comparison.png",
    dpi=300
)
plt.close()

print("Required visualizations generated successfully.")
print("Charts saved in:", OUTPUT_DIR)
