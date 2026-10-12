```sql
-- Mamaearth Capstone: Seed Data
-- Run from the project root using the SQLite command-line tool.
-- First create the tables using sql/schema.sql.

.mode csv
.import --skip 1 data/customers.csv customers
.import --skip 1 data/products.csv products
.import --skip 1 data/orders.csv orders

-- Verify imported row counts
SELECT 'customers' AS table_name, COUNT(*) AS total_rows
FROM customers;

SELECT 'products' AS table_name, COUNT(*) AS total_rows
FROM products;

SELECT 'orders' AS table_name, COUNT(*) AS total_rows
FROM orders;
```