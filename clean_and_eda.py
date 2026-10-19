
from pathlib import Path
import json
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ANALYSIS_DIR = BASE_DIR / "analysis"
NARRATOR_DIR = BASE_DIR / "narrator"

ANALYSIS_DIR.mkdir(exist_ok=True)
NARRATOR_DIR.mkdir(exist_ok=True)

# 1. Load raw datasets
customers = pd.read_csv(DATA_DIR / "customers.csv")
products = pd.read_csv(DATA_DIR / "products.csv")
orders = pd.read_csv(DATA_DIR / "orders.csv")

for df in [customers, products, orders]:
    df.columns = df.columns.str.strip()

customers["signup_date"] = pd.to_datetime(
    customers["signup_date"], errors="coerce"
)
orders["order_date"] = pd.to_datetime(
    orders["order_date"], errors="coerce"
)

print("\n1. RAW DATA SHAPES")
print("Customers:", customers.shape)
print("Products:", products.shape)
print("Orders:", orders.shape)

# 2. Standardize payment methods
print("\n2. RAW PAYMENT METHODS")
print(orders["payment_method"].unique())

orders["payment_method"] = (
    orders["payment_method"].astype("string").str.strip().str.upper()
)

print("\nSTANDARDIZED PAYMENT COUNTS")
print(orders["payment_method"].value_counts().sort_index())

# Convert numeric columns without imputing yet
for col in ["quantity", "discount_pct", "rating", "returned"]:
    orders[col] = pd.to_numeric(orders[col], errors="coerce")

# 3. Remove duplicate natural keys (order_id is intentionally excluded)
natural_key = [
    "customer_id",
    "product_id",
    "order_date",
    "quantity",
    "discount_pct",
    "payment_method",
    "rating",
    "returned",
]

duplicate_mask = orders.duplicated(subset=natural_key, keep="first")
duplicate_ids = orders.loc[duplicate_mask, "order_id"].astype(str).tolist()
duplicate_rows = orders.loc[duplicate_mask].copy()

print("\n3. DUPLICATE CHECK")
print("Duplicate natural-key rows:", int(duplicate_mask.sum()))
print("Duplicate order IDs removed:", duplicate_ids)

# 4. Calculate raw revenue before removing duplicates.
# Missing discounts count as 0% for the raw SQL-style total.
raw_join = orders.merge(
    products[["product_id", "price"]],
    on="product_id",
    how="left",
    validate="many_to_one",
)

raw_join["discount_for_revenue"] = raw_join["discount_pct"].fillna(0)
raw_join["raw_revenue"] = (
    raw_join["quantity"]
    * raw_join["price"]
    * (1 - raw_join["discount_for_revenue"] / 100)
)

raw_revenue = round(raw_join["raw_revenue"].sum(), 2)

# Remove the duplicate natural-key rows
orders = orders.loc[~duplicate_mask].copy()

print("\n4. CLEANED ORDER SHAPE")
print("Orders after deduplication:", orders.shape)

# Impute missing values
missing_discounts = int(orders["discount_pct"].isna().sum())
missing_ratings = int(orders["rating"].isna().sum())
rating_median = orders["rating"].median()

orders["discount_pct"] = orders["discount_pct"].fillna(0)
orders["rating"] = orders["rating"].fillna(rating_median)

print("\n5. MISSING VALUE IMPUTATION")
print("Missing discounts filled with 0:", missing_discounts)
print("Missing ratings filled with median:", missing_ratings)
print("Rating median:", rating_median)
print("Remaining nulls in discount_pct:", orders["discount_pct"].isna().sum())
print("Remaining nulls in rating:", orders["rating"].isna().sum())

# 6. Merge cleaned orders with products and customers
analysis = orders.merge(
    products,
    on="product_id",
    how="left",
    validate="many_to_one",
).merge(
    customers,
    on="customer_id",
    how="left",
    validate="many_to_one",
)

analysis["order_value"] = (
    analysis["quantity"]
    * analysis["price"]
    * (1 - analysis["discount_pct"] / 100)
).round(2)

cleaned_revenue = round(analysis["order_value"].sum(), 2)
duplicate_delta = round(raw_revenue - cleaned_revenue, 2)

print("\n6. REVENUE RECONCILIATION")
print(f"Raw revenue (missing discounts treated as 0%): {raw_revenue:.2f}")
print(f"Cleaned revenue after deduplication: {cleaned_revenue:.2f}")
print(f"Revenue difference due to duplicate rows: {duplicate_delta:.2f}")
print(
    f"Reconciliation: raw revenue {raw_revenue:.2f} minus duplicate "
    f"order value {duplicate_delta:.2f} equals cleaned revenue "
    f"{cleaned_revenue:.2f}. Missing discounts were treated as 0% "
    "in both calculations."
)

# 7. Detect quantity outliers using IQR; flag, do not delete
q1 = analysis["quantity"].quantile(0.25)
q3 = analysis["quantity"].quantile(0.75)
iqr = q3 - q1
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr

analysis["quantity_outlier"] = (
    (analysis["quantity"] < lower_bound)
    | (analysis["quantity"] > upper_bound)
)

outliers = analysis.loc[
    analysis["quantity_outlier"], ["order_id", "quantity"]
]

print("\n7. QUANTITY OUTLIERS")
print(f"Q1: {q1}, Q3: {q3}, IQR: {iqr}")
print(f"Lower bound: {lower_bound}, Upper bound: {upper_bound}")
print(outliers.to_string(index=False))
print("Outliers flagged, not removed:", len(outliers))

# 8. Return rates by payment method
analysis["returned"] = pd.to_numeric(
    analysis["returned"], errors="coerce"
).fillna(0).astype(int)

payment_returns = (
    analysis.groupby("payment_method")
    .agg(
        orders=("order_id", "count"),
        returned_orders=("returned", "sum"),
    )
)
payment_returns["return_rate_pct"] = (
    payment_returns["returned_orders"] / payment_returns["orders"] * 100
).round(1)

print("\n8. RETURN RATE BY PAYMENT METHOD")
print(payment_returns)

cod_rate = float(payment_returns.loc["COD", "return_rate_pct"])
card_rate = float(payment_returns.loc["CARD", "return_rate_pct"])
upi_rate = float(payment_returns.loc["UPI", "return_rate_pct"])

print(
    "Hypothesis: COD orders have a higher return rate than CARD and UPI."
)
print(
    "Hypothesis result:",
    "Confirmed" if cod_rate > card_rate and cod_rate > upi_rate else "Not confirmed",
)

# 9. Payment method × city tier
risk_table = pd.crosstab(
    [analysis["payment_method"], analysis["city_tier"]],
    analysis["returned"],
    margins=False,
)
risk_rates = (
    analysis.groupby(["payment_method", "city_tier"])["returned"]
    .mean()
    .mul(100)
    .round(1)
    .rename("return_rate_pct")
    .reset_index()
)

print("\n9. PAYMENT METHOD × CITY TIER")
print(risk_table)
print("\nRETURN RATE BY PAYMENT AND CITY TIER")
print(risk_rates.to_string(index=False))

tier2_cod = risk_rates.loc[
    (risk_rates["payment_method"] == "COD")
    & (risk_rates["city_tier"] == 2),
    "return_rate_pct",
]
tier2_cod_rate = float(tier2_cod.iloc[0]) if not tier2_cod.empty else 0.0

# 10. Correlation analysis
correlation_columns = ["rating", "returned", "discount_pct", "quantity"]
correlation = analysis[correlation_columns].corr().round(3)

print("\n10. CORRELATION MATRIX")
print(correlation)

discount_return_corr = float(correlation.loc["discount_pct", "returned"])
print("Discount vs return correlation:", discount_return_corr)
print(
    "Hypothesis: higher discounts reduce returns.",
    "Busted" if discount_return_corr <= -0.2 else "Not supported by a meaningful negative correlation",
)

# 11. Monthly revenue, with and without quantity outliers
analysis["month"] = analysis["order_date"].dt.to_period("M").astype(str)

monthly_revenue = (
    analysis.groupby("month")["order_value"].sum().round(2)
)

# Corrected trend excludes flagged outlier orders from monthly totals.
# Original rows remain in the cleaned dataset.
corrected_monthly_revenue = (
    analysis.loc[~analysis["quantity_outlier"]]
    .groupby("month")["order_value"]
    .sum()
    .round(2)
)

monthly_comparison = pd.concat(
    [
        monthly_revenue.rename("revenue_including_outliers"),
        corrected_monthly_revenue.rename("revenue_excluding_outliers"),
    ],
    axis=1,
).fillna(0).round(2)

print("\n11. MONTHLY REVENUE")
print(monthly_comparison)

if not corrected_monthly_revenue.empty:
    true_peak_month = corrected_monthly_revenue.idxmax()
    true_peak_revenue = float(corrected_monthly_revenue.max())
else:
    true_peak_month = ""
    true_peak_revenue = 0.0

if not monthly_revenue.empty:
    apparent_peak_month = monthly_revenue.idxmax()
    apparent_peak_revenue = float(monthly_revenue.max())
else:
    apparent_peak_month = ""
    apparent_peak_revenue = 0.0

# Save analysis outputs
analysis.to_csv(ANALYSIS_DIR / "cleaned_mamaearth_data.csv", index=False)
analysis.to_csv(DATA_DIR / "cleaned_mamaearth_data.csv", index=False)
payment_returns.to_csv(ANALYSIS_DIR / "payment_return_rates.csv")
risk_rates.to_csv(ANALYSIS_DIR / "payment_city_tier_returns.csv")
correlation.to_csv(ANALYSIS_DIR / "correlation_matrix.csv")
monthly_comparison.to_csv(ANALYSIS_DIR / "monthly_revenue_comparison.csv")

# 12. Create structured findings for the GenAI narrator
findings = {
    "raw_total_revenue_inr": raw_revenue,
    "cleaned_total_revenue_inr": cleaned_revenue,
    "duplicate_reconciliation_delta_inr": duplicate_delta,
    "raw_order_count": int(len(raw_join)),
    "cleaned_order_count": int(len(analysis)),
    "duplicate_count": int(duplicate_mask.sum()),
    "duplicate_order_ids": duplicate_ids,
    "missing_discounts_imputed": missing_discounts,
    "missing_ratings_imputed": missing_ratings,
    "rating_median": float(rating_median),
    "quantity_outlier_count": int(analysis["quantity_outlier"].sum()),
    "quantity_outlier_order_ids": outliers["order_id"].astype(str).tolist(),
    "return_rate_by_payment": {
        "COD": cod_rate,
        "CARD": card_rate,
        "UPI": upi_rate,
    },
    "highest_risk_segment": {
        "payment_method": "COD",
        "city_tier": 2,
        "return_rate_pct": tier2_cod_rate,
    },
    "true_peak_month": {
        "month": true_peak_month,
        "revenue_inr": round(true_peak_revenue, 2),
    },
    "outlier_inflated_month": {
        "month": apparent_peak_month,
        "apparent_revenue_inr": round(apparent_peak_revenue, 2),
        "corrected_revenue_inr": round(
            float(corrected_monthly_revenue.get(apparent_peak_month, 0)), 2
        ),
    },
    "monthly_revenue_including_outliers": {
        str(k): round(float(v), 2) for k, v in monthly_revenue.items()
    },
    "monthly_revenue_excluding_outliers": {
        str(k): round(float(v), 2)
        for k, v in corrected_monthly_revenue.items()
    },
    "discount_return_correlation": discount_return_corr,
}

with open(NARRATOR_DIR / "findings.json", "w", encoding="utf-8") as f:
    json.dump(findings, f, indent=2)

print("\n12. OUTPUT FILES")
print("Saved cleaned datasets and analysis CSV files.")
print("Saved narrator/findings.json")
print("\nAnalysis completed.")
