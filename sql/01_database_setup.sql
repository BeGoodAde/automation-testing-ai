-- E-commerce Analytics Database Setup
-- Creates database, tables, and initial configuration

-- Create database (run this separately if needed)
-- CREATE DATABASE ecommerce_analytics_2025;

-- Connect to the database
\c ecommerce_analytics_2025;

-- Create extension for additional functions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Drop tables if they exist (for clean restart)
DROP TABLE IF EXISTS sales CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS sales_summary CASCADE;

-- Create customers table
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_segment VARCHAR(20) NOT NULL,
    country VARCHAR(50) NOT NULL,
    first_order_date DATE,
    last_order_date DATE,
    total_orders INTEGER DEFAULT 0,
    total_spent DECIMAL(12,2) DEFAULT 0.00,
    avg_order_value DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create products table
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(200) UNIQUE NOT NULL,
    category VARCHAR(50) NOT NULL,
    avg_price DECIMAL(10,2),
    total_quantity_sold INTEGER DEFAULT 0,
    total_revenue DECIMAL(12,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create main sales table with enhanced structure
CREATE TABLE sales (
    order_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price > 0),
    total_value DECIMAL(12,2) NOT NULL,
    order_date DATE NOT NULL,
    customer_id INTEGER NOT NULL,
    country VARCHAR(50) NOT NULL,
    customer_segment VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_total_value CHECK (total_value = quantity * unit_price),
    CONSTRAINT chk_order_date CHECK (order_date >= '2024-01-01' AND order_date <= '2025-12-31'),
    CONSTRAINT chk_customer_segment CHECK (customer_segment IN ('Premium', 'Regular', 'Bargain'))
);

-- Create sales summary table for aggregated analytics
CREATE TABLE sales_summary (
    summary_id SERIAL PRIMARY KEY,
    summary_date DATE NOT NULL,
    summary_type VARCHAR(20) NOT NULL, -- 'daily', 'weekly', 'monthly'
    category VARCHAR(50),
    country VARCHAR(50),
    customer_segment VARCHAR(20),
    total_orders INTEGER DEFAULT 0,
    total_revenue DECIMAL(12,2) DEFAULT 0.00,
    avg_order_value DECIMAL(10,2) DEFAULT 0.00,
    unique_customers INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(summary_date, summary_type, category, country, customer_segment)
);

-- Create indexes for better performance
CREATE INDEX idx_sales_order_date ON sales(order_date);
CREATE INDEX idx_sales_customer_id ON sales(customer_id);
CREATE INDEX idx_sales_category ON sales(category);
CREATE INDEX idx_sales_country ON sales(country);
CREATE INDEX idx_sales_customer_segment ON sales(customer_segment);
CREATE INDEX idx_sales_total_value ON sales(total_value);

-- Composite indexes for common queries
CREATE INDEX idx_sales_date_category ON sales(order_date, category);
CREATE INDEX idx_sales_date_country ON sales(order_date, country);
CREATE INDEX idx_sales_customer_date ON sales(customer_id, order_date);

-- Indexes for summary table
CREATE INDEX idx_summary_date_type ON sales_summary(summary_date, summary_type);
CREATE INDEX idx_summary_category ON sales_summary(category);

-- Create views for common analytics
CREATE OR REPLACE VIEW v_monthly_sales AS
SELECT 
    DATE_TRUNC('month', order_date) AS month,
    category,
    COUNT(*) AS total_orders,
    SUM(quantity) AS total_quantity,
    SUM(total_value) AS total_revenue,
    AVG(total_value) AS avg_order_value,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM sales
GROUP BY DATE_TRUNC('month', order_date), category
ORDER BY month, total_revenue DESC;

CREATE OR REPLACE VIEW v_customer_analytics AS
SELECT 
    customer_id,
    customer_segment,
    country,
    COUNT(*) AS total_orders,
    SUM(total_value) AS total_spent,
    AVG(total_value) AS avg_order_value,
    MIN(order_date) AS first_order,
    MAX(order_date) AS last_order,
    MAX(order_date) - MIN(order_date) AS customer_lifetime_days
FROM sales
GROUP BY customer_id, customer_segment, country
ORDER BY total_spent DESC;

CREATE OR REPLACE VIEW v_product_performance AS
SELECT 
    product_name,
    category,
    COUNT(*) AS times_ordered,
    SUM(quantity) AS total_quantity_sold,
    SUM(total_value) AS total_revenue,
    AVG(unit_price) AS avg_price,
    AVG(quantity) AS avg_quantity_per_order
FROM sales
GROUP BY product_name, category
ORDER BY total_revenue DESC;

-- Create function to update customer aggregates
CREATE OR REPLACE FUNCTION update_customer_aggregates()
RETURNS VOID AS $$
BEGIN
    -- Insert or update customer aggregates
    INSERT INTO customers (customer_id, customer_segment, country, first_order_date, last_order_date, total_orders, total_spent, avg_order_value)
    SELECT 
        customer_id,
        customer_segment,
        country,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date,
        COUNT(*) AS total_orders,
        SUM(total_value) AS total_spent,
        AVG(total_value) AS avg_order_value
    FROM sales
    GROUP BY customer_id, customer_segment, country
    ON CONFLICT (customer_id) DO UPDATE SET
        customer_segment = EXCLUDED.customer_segment,
        country = EXCLUDED.country,
        first_order_date = EXCLUDED.first_order_date,
        last_order_date = EXCLUDED.last_order_date,
        total_orders = EXCLUDED.total_orders,
        total_spent = EXCLUDED.total_spent,
        avg_order_value = EXCLUDED.avg_order_value,
        updated_at = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Create function to update product aggregates
CREATE OR REPLACE FUNCTION update_product_aggregates()
RETURNS VOID AS $$
BEGIN
    -- Insert or update product aggregates
    INSERT INTO products (product_name, category, avg_price, total_quantity_sold, total_revenue)
    SELECT 
        product_name,
        category,
        AVG(unit_price) AS avg_price,
        SUM(quantity) AS total_quantity_sold,
        SUM(total_value) AS total_revenue
    FROM sales
    GROUP BY product_name, category
    ON CONFLICT (product_name) DO UPDATE SET
        category = EXCLUDED.category,
        avg_price = EXCLUDED.avg_price,
        total_quantity_sold = EXCLUDED.total_quantity_sold,
        total_revenue = EXCLUDED.total_revenue,
        updated_at = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update aggregates
CREATE OR REPLACE FUNCTION trigger_update_aggregates()
RETURNS TRIGGER AS $$
BEGIN
    -- This would be called after significant data changes
    -- For performance, we'll call these manually or via scheduled jobs
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO analytics_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO analytics_user;

-- Add comments for documentation
COMMENT ON TABLE sales IS 'Main sales transaction table with detailed order information';
COMMENT ON TABLE customers IS 'Customer aggregation table with summary statistics';
COMMENT ON TABLE products IS 'Product aggregation table with performance metrics';
COMMENT ON TABLE sales_summary IS 'Pre-calculated summary statistics for faster reporting';

COMMENT ON VIEW v_monthly_sales IS 'Monthly sales aggregation by category';
COMMENT ON VIEW v_customer_analytics IS 'Customer behavior and value analysis';
COMMENT ON VIEW v_product_performance IS 'Product sales performance metrics';

-- Display table information
\dt
\dv

-- Show table sizes (will be empty until data is loaded)
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public' 
ORDER BY tablename, attname;

PRINT 'Database setup completed successfully!';
PRINT 'Next step: Run the data import script to load CSV data.';