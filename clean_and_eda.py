from pathlib import Path
import pandas as pd

# Project folders
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Load datasets
customers = pd.read_csv(DATA_DIR / "customers.csv")
products = pd.read_csv(DATA_DIR / "products.csv")
orders = pd.read_csv(DATA_DIR / "orders.csv")

# Clean column names and duplicate rows
for df in [customers, products, orders]:
    df.columns = df.columns.str.strip()
    df.drop_duplicates(inplace=True)

# Convert dates
for df, column in [
    (customers, "signup_date"),
    (orders, "order_date")
]:
    df[column] = pd.to_datetime(df[column], errors="coerce")

# Handle missing values in important fields
orders.dropna(subset=["order_id", "customer_id", "product_id"], inplace=True)

# Merge datasets for analysis
analysis = orders.merge(
    products, on="product_id", how="left"
).merge(
    customers, on="customer_id", how="left"
)

# Calculate revenue after discount
# Keep revenue missing when discount information is unavailable
analysis["discount_pct"] = pd.to_numeric(
    analysis["discount_pct"], errors="coerce"
)
analysis["revenue"] = (
    analysis["quantity"] * analysis["price"]
    * (1 - analysis["discount_pct"] / 100)
).round(2)

# Detect quantity outliers using IQR
q1 = analysis["quantity"].quantile(0.25)
q3 = analysis["quantity"].quantile(0.75)

iqr = q3 - q1
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr

analysis["quantity_outlier"] = (
    (analysis["quantity"] < lower_bound)
    | (analysis["quantity"] > upper_bound)
)

# Save cleaned analysis dataset
OUTPUT_DIR = BASE_DIR / "analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

output_file = OUTPUT_DIR / "cleaned_mamaearth_data.csv"
analysis.to_csv(output_file, index=False)

print("Data cleaning and analysis completed successfully!")
print(f"Customers loaded: {len(customers)}")
print(f"Products loaded: {len(products)}")
print(f"Orders analysed: {len(analysis)}")
print(f"Quantity outliers: {analysis['quantity_outlier'].sum()}")
print(f"Output saved to: {output_file}")
