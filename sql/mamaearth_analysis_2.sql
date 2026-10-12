SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM orders_import_temp;
SELECT order_id
FROM orders
ORDER BY order_id;
WITH RECURSIVE numbers AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1
    FROM numbers
    WHERE n < 180
)
SELECT CONCAT('O', LPAD(numbers.n, 4, '0')) AS missing_order_id
FROM numbers
LEFT JOIN orders
    ON orders.order_id = CONCAT('O', LPAD(numbers.n, 4, '0'))
WHERE orders.order_id IS NULL
ORDER BY numbers.n;