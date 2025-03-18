-- Create database
CREATE DATABASE IF NOT EXISTS ecommerce_analysis;
USE ecommerce_analysis;

-- Create transactions table
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    transaction_date DATETIME,
    product_id VARCHAR(50),
    product_category VARCHAR(100),
    quantity INT,
    unit_price DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    country VARCHAR(100),
    payment_method VARCHAR(50),
    customer_age INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create customer segments table
CREATE TABLE IF NOT EXISTS customer_segments (
    customer_id VARCHAR(50) PRIMARY KEY,
    segment_name VARCHAR(50),
    rfm_score INT,
    cluster_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES transactions(customer_id)
);

-- Create product recommendations table
CREATE TABLE IF NOT EXISTS product_recommendations (
    product_id VARCHAR(50),
    recommended_product_id VARCHAR(50),
    confidence_score DECIMAL(5,2),
    support_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id, recommended_product_id)
);

-- Create predictive models table
CREATE TABLE IF NOT EXISTS predictive_models (
    model_id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100),
    model_type VARCHAR(50),
    accuracy_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_transaction_date ON transactions(transaction_date);
CREATE INDEX idx_customer_id ON transactions(customer_id);
CREATE INDEX idx_product_category ON transactions(product_category);
CREATE INDEX idx_country ON transactions(country); 