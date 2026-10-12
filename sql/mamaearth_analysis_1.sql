CREATE DATABASE IF NOT EXISTS mamaearth_db;

USE mamaearth_db;

CREATE TABLE customers (
    customer_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100),
    city VARCHAR(50),
    city_tier INT,
    signup_date DATE,
    acquisition_source VARCHAR(50)
);

CREATE TABLE products (
    product_id VARCHAR(10) PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10,2)
);

CREATE TABLE orders (
    order_id VARCHAR(10) PRIMARY KEY,
    customer_id VARCHAR(10),
    product_id VARCHAR(10),
    order_date DATE,
    quantity INT,
    discount_pct DECIMAL(5,2),
    payment_method VARCHAR(20),
    rating DECIMAL(3,1),
    returned INT,

    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
