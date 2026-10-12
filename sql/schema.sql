```sql
-- Mamaearth Capstone: Database Schema
-- SQLite-compatible schema

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT,
    city TEXT,
    city_tier INTEGER,
    signup_date TEXT,
    acquisition_source TEXT
);

CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    price REAL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT,
    product_id TEXT,
    order_date TEXT,
    quantity INTEGER,
    discount_pct REAL,
    payment_method TEXT,
    rating REAL,
    returned INTEGER,
    quantity_outlier INTEGER,
    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),
    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);
```