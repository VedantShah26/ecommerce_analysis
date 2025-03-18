-- Sales Analysis by Country
SELECT 
    country,
    COUNT(DISTINCT transaction_id) as total_transactions,
    SUM(total_amount) as total_sales,
    AVG(total_amount) as avg_transaction_value
FROM transactions
GROUP BY country
ORDER BY total_sales DESC;

-- Product Category Performance
SELECT 
    product_category,
    COUNT(DISTINCT transaction_id) as total_transactions,
    SUM(total_amount) as total_sales,
    AVG(quantity) as avg_quantity
FROM transactions
GROUP BY product_category
ORDER BY total_sales DESC;

-- Customer Age Distribution
SELECT 
    CASE 
        WHEN customer_age < 25 THEN '18-24'
        WHEN customer_age BETWEEN 25 AND 34 THEN '25-34'
        WHEN customer_age BETWEEN 35 AND 44 THEN '35-44'
        WHEN customer_age BETWEEN 45 AND 54 THEN '45-54'
        ELSE '55+'
    END as age_group,
    COUNT(DISTINCT customer_id) as customer_count,
    AVG(total_amount) as avg_purchase_amount
FROM transactions
GROUP BY 
    CASE 
        WHEN customer_age < 25 THEN '18-24'
        WHEN customer_age BETWEEN 25 AND 34 THEN '25-34'
        WHEN customer_age BETWEEN 35 AND 44 THEN '35-44'
        WHEN customer_age BETWEEN 45 AND 54 THEN '45-54'
        ELSE '55+'
    END
ORDER BY age_group;

-- Payment Method Analysis
SELECT 
    payment_method,
    COUNT(DISTINCT transaction_id) as transaction_count,
    SUM(total_amount) as total_amount,
    AVG(total_amount) as avg_amount
FROM transactions
GROUP BY payment_method
ORDER BY total_amount DESC;

-- Customer Segment Analysis
SELECT 
    cs.segment_name,
    COUNT(DISTINCT t.customer_id) as customer_count,
    AVG(t.total_amount) as avg_purchase_amount,
    COUNT(DISTINCT t.transaction_id) as total_transactions
FROM customer_segments cs
JOIN transactions t ON cs.customer_id = t.customer_id
GROUP BY cs.segment_name
ORDER BY avg_purchase_amount DESC;

-- Top Product Recommendations
SELECT 
    t1.product_category as product,
    t2.product_category as recommended_product,
    pr.confidence_score,
    pr.support_score
FROM product_recommendations pr
JOIN transactions t1 ON pr.product_id = t1.product_id
JOIN transactions t2 ON pr.recommended_product_id = t2.product_id
WHERE pr.confidence_score > 0.5
ORDER BY pr.confidence_score DESC
LIMIT 10;

-- Model Performance Comparison
SELECT 
    model_name,
    model_type,
    accuracy_score,
    created_at
FROM predictive_models
ORDER BY accuracy_score DESC; 