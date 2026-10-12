```sql
-- Mamaearth Capstone: Business Analysis Reports
-- SQLite-compatible queries

-- 1. Total number of orders
SELECT COUNT(*) AS total_orders
FROM orders;

-- 2. Total revenue by product category
SELECT p.category,
       ROUND(SUM(o.quantity * p.price *
       (1 - o.discount_pct / 100.0)), 2) AS total_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;

-- 3. Category-wise return rate
SELECT p.category,
       COUNT(*) AS total_orders,
       SUM(CASE WHEN o.returned = 1 THEN 1 ELSE 0 END)
           AS returned_orders,
       ROUND(
           100.0 * SUM(CASE WHEN o.returned = 1 THEN 1 ELSE 0 END)
           / COUNT(*), 2
       ) AS return_rate_pct
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY return_rate_pct DESC;

-- 4. Monthly revenue
SELECT strftime('%Y-%m', o.order_date) AS month,
       ROUND(SUM(o.quantity * p.price *
       (1 - o.discount_pct / 100.0)), 2) AS monthly_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY strftime('%Y-%m', o.order_date)
ORDER BY month;

-- 5. Average customer rating by category
SELECT p.category,
       ROUND(AVG(o.rating), 2) AS average_rating
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY average_rating DESC;

-- 6. Total revenue across all orders
SELECT ROUND(SUM(o.quantity * p.price *
       (1 - o.discount_pct / 100.0)), 2) AS total_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id;

-- 7. Top 5 products by revenue
SELECT p.product_name,
       ROUND(SUM(o.quantity * p.price *
       (1 - o.discount_pct / 100.0)), 2) AS revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY revenue DESC
LIMIT 5;

-- 8. Payment method usage
SELECT payment_method, COUNT(*) AS total_orders
FROM orders
GROUP BY payment_method
ORDER BY total_orders DESC;

-- 9. Overall return rate
SELECT COUNT(*) AS total_orders,
       SUM(CASE WHEN returned = 1 THEN 1 ELSE 0 END)
           AS returned_orders,
       ROUND(
           100.0 * SUM(CASE WHEN returned = 1 THEN 1 ELSE 0 END)
           / COUNT(*), 2
       ) AS return_rate_pct
FROM orders;
```