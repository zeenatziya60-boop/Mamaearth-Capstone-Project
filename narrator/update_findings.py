
from pathlib import Path
import json
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "cleaned_mamaearth_data.csv"
OUTPUT_FILE = BASE_DIR / "narrator" / "findings.json"

df = pd.read_csv(DATA_FILE)
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

total_orders = len(df)
total_revenue = round(df["revenue"].sum(), 2)
return_rate = round(df["returned"].mean() * 100, 2)

category_analysis = []

for category, group in df.groupby("category"):
    category_analysis.append({
        "category": category,
        "total_revenue": round(group["revenue"].sum(), 2),
        "total_orders": int(len(group)),
        "returned_orders": int(group["returned"].sum()),
        "average_rating": (
            round(group["rating"].mean(), 2)
            if group["rating"].notna().any() else None
        ),
        "return_rate_pct": round(group["returned"].mean() * 100, 2)
    })

monthly = (
    df.assign(month=df["order_date"].dt.to_period("M").astype(str))
    .groupby("month")["revenue"]
    .sum()
)

monthly_revenue = [
    {"month": month, "revenue": round(float(revenue), 2)}
    for month, revenue in monthly.items()
]

findings = {
    "total_revenue": total_revenue,
    "total_orders": total_orders,
    "overall_return_rate_pct": return_rate,
    "missing_discount_orders": int(df["discount_pct"].isna().sum()),
    "category_analysis": category_analysis,
    "monthly_revenue": monthly_revenue,
    "highest_revenue_month": (
        str(monthly.idxmax()) if monthly.notna().any() else None
    ),
    "highest_revenue_category": max(
        category_analysis,
        key=lambda x: x["total_revenue"]
    )["category"],
    "highest_return_rate_category": max(
        category_analysis,
        key=lambda x: x["return_rate_pct"]
    )["category"]
}

OUTPUT_FILE.write_text(
    json.dumps(findings, indent=4),
    encoding="utf-8"
)

print("Findings updated successfully!")
print("Total orders:", total_orders)
print("Known revenue:", total_revenue)
print("Missing discount orders:", findings["missing_discount_orders"])
print("Overall return rate:", return_rate, "%")
print("Saved to:", OUTPUT_FILE)
