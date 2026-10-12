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
analysis["revenue"] = (
    analysis["quantity"] * analysis["price"]
    * (1 - analysis["discount_pct"] / 100)
).round(2)

# Detect quantity outliers using IQR
q1 = analysis["quantity"].quantile(0.25)
q3 = analysis["quantity"].quantile(0.75)
