-- Advanced E-commerce Analytics Queries
-- Comprehensive SQL analysis for business insights

-- Set up query optimization
SET work_mem = '256MB';
SET shared_buffers = '128MB';

-- ============================================
-- SECTION 1: SALES PERFORMANCE ANALYSIS
-- ============================================

-- 1.1 Overall Sales Performance
SELECT 
    'Overall Performance' as metric_type,
    COUNT(*) as total_orders,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(DISTINCT product_name) as unique_products,
    SUM(total_value) as total_revenue,
    AVG(total_value) as avg_order_value,
    SUM(quantity) as total_units_sold,
    MIN(order_date) as first_order,
    MAX(order_date) as last_order
FROM sales;

-- 1.2 Sales by Category with Growth Analysis
WITH category_monthly AS (
    SELECT 
        category,
        DATE_TRUNC('month', order_date) as month,
        SUM(total_value) as monthly_revenue,
        COUNT(*) as monthly_orders
    FROM sales
    GROUP BY category, DATE_TRUNC('month', order_date)
),
category_growth AS (
    SELECT 
        category,
        month,
        monthly_revenue,
        monthly_orders,
        LAG(monthly_revenue) OVER (PARTITION BY category ORDER BY month) as prev_month_revenue,
        ROUND(
            ((monthly_revenue - LAG(monthly_revenue) OVER (PARTITION BY category ORDER BY month)) / 
             NULLIF(LAG(monthly_revenue) OVER (PARTITION BY category ORDER BY month), 0) * 100), 2
        ) as revenue_growth_pct
    FROM category_monthly
)
SELECT 
    category,
    COUNT(*) as months_active,
    SUM(monthly_revenue) as total_revenue,
    AVG(monthly_revenue) as avg_monthly_revenue,
    AVG(revenue_growth_pct) as avg_growth_rate,
    MAX(monthly_revenue) as peak_monthly_revenue,
    MIN(monthly_revenue) as lowest_monthly_revenue
FROM category_growth
GROUP BY category
ORDER BY total_revenue DESC;

-- 1.3 Top Performing Products
SELECT 
    product_name,
    category,
    COUNT(*) as times_ordered,
    SUM(quantity) as total_quantity_sold,
    SUM(total_value) as total_revenue,
    AVG(unit_price) as avg_price,
    ROUND(AVG(total_value), 2) as avg_order_value,
    COUNT(DISTINCT customer_id) as unique_customers,
    ROUND(SUM(total_value) / COUNT(DISTINCT customer_id), 2) as revenue_per_customer
FROM sales
GROUP BY product_name, category
HAVING COUNT(*) >= 10  -- Products with at least 10 orders
ORDER BY total_revenue DESC
LIMIT 20;

-- ============================================
-- SECTION 2: CUSTOMER SEGMENTATION & ANALYSIS
-- ============================================

-- 2.1 RFM Analysis (Recency, Frequency, Monetary)
WITH customer_rfm AS (
    SELECT 
        customer_id,
        customer_segment,
        country,
        MAX(order_date) as last_order_date,
        CURRENT_DATE - MAX(order_date) as recency_days,
        COUNT(*) as frequency,
        SUM(total_value) as monetary_value,
        AVG(total_value) as avg_order_value
    FROM sales
    GROUP BY customer_id, customer_segment, country
),
rfm_scores AS (
    SELECT 
        *,
        NTILE(5) OVER (ORDER BY recency_days DESC) as recency_score,
        NTILE(5) OVER (ORDER BY frequency) as frequency_score,
        NTILE(5) OVER (ORDER BY monetary_value) as monetary_score
    FROM customer_rfm
),
rfm_segments AS (
    SELECT 
        *,
        CONCAT(recency_score, frequency_score, monetary_score) as rfm_code,
        CASE 
            WHEN recency_score >= 4 AND frequency_score >= 4 AND monetary_score >= 4 THEN 'Champions'
            WHEN recency_score >= 3 AND frequency_score >= 3 AND monetary_score >= 3 THEN 'Loyal Customers'
            WHEN recency_score >= 3 AND frequency_score <= 2 AND monetary_score >= 3 THEN 'Potential Loyalists'
            WHEN recency_score >= 4 AND frequency_score <= 2 AND monetary_score <= 2 THEN 'New Customers'
            WHEN recency_score <= 2 AND frequency_score >= 3 AND monetary_value >= 3 THEN 'At Risk'
            WHEN recency_score <= 2 AND frequency_score <= 2 AND monetary_value >= 4 THEN 'Cannot Lose Them'
            WHEN recency_score <= 2 AND frequency_score <= 2 AND monetary_value <= 2 THEN 'Lost'
            ELSE 'Others'
        END as rfm_segment
    FROM rfm_scores
)
SELECT 
    rfm_segment,
    COUNT(*) as customer_count,
    ROUND(AVG(recency_days), 1) as avg_recency_days,
    ROUND(AVG(frequency), 1) as avg_frequency,
    ROUND(AVG(monetary_value), 2) as avg_monetary_value,
    ROUND(SUM(monetary_value), 2) as total_revenue,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage_of_customers
FROM rfm_segments
GROUP BY rfm_segment
ORDER BY total_revenue DESC;

-- 2.2 Customer Lifetime Value Analysis
WITH customer_metrics AS (
    SELECT 
        customer_id,
        customer_segment,
        country,
        MIN(order_date) as first_order,
        MAX(order_date) as last_order,
        COUNT(*) as total_orders,
        SUM(total_value) as total_spent,
        AVG(total_value) as avg_order_value,
        MAX(order_date) - MIN(order_date) as customer_lifetime_days
    FROM sales
    GROUP BY customer_id, customer_segment, country
),
clv_analysis AS (
    SELECT 
        *,
        CASE 
            WHEN customer_lifetime_days = 0 THEN total_spent
            ELSE ROUND(total_spent * 365.0 / customer_lifetime_days, 2)
        END as annualized_value,
        CASE
            WHEN total_spent >= 1000 THEN 'High Value'
            WHEN total_spent >= 300 THEN 'Medium Value'
            ELSE 'Low Value'
        END as value_segment
    FROM customer_metrics
)
SELECT 
    value_segment,
    customer_segment,
    COUNT(*) as customer_count,
    ROUND(AVG(total_spent), 2) as avg_total_spent,
    ROUND(AVG(total_orders), 1) as avg_total_orders,
    ROUND(AVG(avg_order_value), 2) as avg_order_value,
    ROUND(AVG(customer_lifetime_days), 1) as avg_lifetime_days,
    ROUND(AVG(annualized_value), 2) as avg_annualized_value,
    ROUND(SUM(total_spent), 2) as segment_total_revenue
FROM clv_analysis
GROUP BY value_segment, customer_segment
ORDER BY segment_total_revenue DESC;

-- ============================================
-- SECTION 3: TIME SERIES ANALYSIS
-- ============================================

-- 3.1 Daily Sales Trends with Moving Averages
WITH daily_sales AS (
    SELECT 
        order_date,
        COUNT(*) as daily_orders,
        SUM(total_value) as daily_revenue,
        COUNT(DISTINCT customer_id) as daily_customers,
        AVG(total_value) as daily_avg_order_value
    FROM sales
    GROUP BY order_date
    ORDER BY order_date
),
sales_with_ma AS (
    SELECT 
        *,
        AVG(daily_revenue) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as revenue_7day_ma,
        AVG(daily_revenue) OVER (ORDER BY order_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) as revenue_30day_ma,
        LAG(daily_revenue, 7) OVER (ORDER BY order_date) as revenue_7days_ago
    FROM daily_sales
)
SELECT 
    order_date,
    daily_orders,
    daily_revenue,
    daily_customers,
    ROUND(daily_avg_order_value, 2) as daily_avg_order_value,
    ROUND(revenue_7day_ma, 2) as revenue_7day_moving_avg,
    ROUND(revenue_30day_ma, 2) as revenue_30day_moving_avg,
    ROUND(((daily_revenue - revenue_7days_ago) / NULLIF(revenue_7days_ago, 0) * 100), 2) as week_over_week_growth
FROM sales_with_ma
WHERE order_date >= '2024-02-01'  -- Skip early dates with incomplete moving averages
ORDER BY order_date;

-- 3.2 Seasonal Analysis
SELECT 
    EXTRACT(month FROM order_date) as month,
    TO_CHAR(DATE_TRUNC('month', order_date), 'Month') as month_name,
    COUNT(*) as total_orders,
    SUM(total_value) as total_revenue,
    AVG(total_value) as avg_order_value,
    COUNT(DISTINCT customer_id) as unique_customers,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as pct_of_total_orders,
    ROUND(100.0 * SUM(total_value) / SUM(SUM(total_value)) OVER (), 2) as pct_of_total_revenue
FROM sales
GROUP BY EXTRACT(month FROM order_date), TO_CHAR(DATE_TRUNC('month', order_date), 'Month')
ORDER BY month;

-- 3.3 Weekly Patterns
SELECT 
    EXTRACT(dow FROM order_date) as day_of_week,
    CASE EXTRACT(dow FROM order_date)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END as day_name,
    COUNT(*) as total_orders,
    SUM(total_value) as total_revenue,
    AVG(total_value) as avg_order_value,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as pct_of_total_orders
FROM sales
GROUP BY EXTRACT(dow FROM order_date)
ORDER BY day_of_week;

-- ============================================
-- SECTION 4: GEOGRAPHIC ANALYSIS
-- ============================================

-- 4.1 Country Performance Analysis
SELECT 
    country,
    COUNT(*) as total_orders,
    COUNT(DISTINCT customer_id) as unique_customers,
    SUM(total_value) as total_revenue,
    AVG(total_value) as avg_order_value,
    ROUND(COUNT(*)::NUMERIC / COUNT(DISTINCT customer_id), 2) as orders_per_customer,
    ROUND(100.0 * SUM(total_value) / SUM(SUM(total_value)) OVER (), 2) as revenue_share_pct,
    MIN(order_date) as first_order,
    MAX(order_date) as last_order
FROM sales
GROUP BY country
ORDER BY total_revenue DESC;

-- 4.2 Country-Category Performance Matrix
SELECT 
    country,
    category,
    COUNT(*) as orders,
    SUM(total_value) as revenue,
    AVG(total_value) as avg_order_value,
    ROUND(100.0 * SUM(total_value) / SUM(SUM(total_value)) OVER (PARTITION BY country), 2) as category_share_in_country
FROM sales
GROUP BY country, category
ORDER BY country, revenue DESC;

-- ============================================
-- SECTION 5: COHORT ANALYSIS
-- ============================================

-- 5.1 Customer Acquisition Cohorts
WITH customer_cohorts AS (
    SELECT 
        customer_id,
        DATE_TRUNC('month', MIN(order_date)) as cohort_month
    FROM sales
    GROUP BY customer_id
),
order_cohorts AS (
    SELECT 
        s.customer_id,
        s.order_date,
        s.total_value,
        c.cohort_month,
        DATE_TRUNC('month', s.order_date) as order_month,
        EXTRACT(year FROM AGE(DATE_TRUNC('month', s.order_date), c.cohort_month)) * 12 + 
        EXTRACT(month FROM AGE(DATE_TRUNC('month', s.order_date), c.cohort_month)) as months_since_first_order
    FROM sales s
    JOIN customer_cohorts c ON s.customer_id = c.customer_id
),
cohort_summary AS (
    SELECT 
        cohort_month,
        months_since_first_order,
        COUNT(DISTINCT customer_id) as customers,
        SUM(total_value) as revenue,
        COUNT(*) as orders
    FROM order_cohorts
    GROUP BY cohort_month, months_since_first_order
),
cohort_sizes AS (
    SELECT 
        cohort_month,
        COUNT(DISTINCT customer_id) as cohort_size
    FROM customer_cohorts
    GROUP BY cohort_month
)
SELECT 
    cs.cohort_month,
    css.cohort_size,
    cs.months_since_first_order,
    cs.customers,
    cs.revenue,
    cs.orders,
    ROUND(100.0 * cs.customers / css.cohort_size, 2) as retention_rate,
    ROUND(cs.revenue / cs.customers, 2) as revenue_per_customer
FROM cohort_summary cs
JOIN cohort_sizes css ON cs.cohort_month = css.cohort_month
WHERE cs.months_since_first_order <= 11  -- First 12 months
ORDER BY cs.cohort_month, cs.months_since_first_order;

-- ============================================
-- SECTION 6: ADVANCED BUSINESS METRICS
-- ============================================

-- 6.1 Product Performance with Statistical Analysis
SELECT 
    product_name,
    category,
    COUNT(*) as order_frequency,
    SUM(quantity) as total_units,
    ROUND(AVG(unit_price), 2) as avg_price,
    ROUND(STDDEV(unit_price), 2) as price_stddev,
    ROUND(MIN(unit_price), 2) as min_price,
    ROUND(MAX(unit_price), 2) as max_price,
    SUM(total_value) as total_revenue,
    ROUND(AVG(total_value), 2) as avg_order_value,
    COUNT(DISTINCT customer_id) as unique_customers,
    ROUND(SUM(total_value) / COUNT(DISTINCT customer_id), 2) as revenue_per_customer,
    ROUND(COUNT(*)::NUMERIC / COUNT(DISTINCT customer_id), 2) as repeat_purchase_rate
FROM sales
GROUP BY product_name, category
HAVING COUNT(*) >= 5  -- Products with at least 5 orders
ORDER BY total_revenue DESC
LIMIT 25;

-- 6.2 Customer Churn Risk Analysis
WITH last_orders AS (
    SELECT 
        customer_id,
        MAX(order_date) as last_order_date,
        COUNT(*) as total_orders,
        SUM(total_value) as total_spent,
        CURRENT_DATE - MAX(order_date) as days_since_last_order
    FROM sales
    GROUP BY customer_id
)
SELECT 
    CASE 
        WHEN days_since_last_order <= 30 THEN 'Active (0-30 days)'
        WHEN days_since_last_order <= 60 THEN 'At Risk (31-60 days)'
        WHEN days_since_last_order <= 90 THEN 'Churning (61-90 days)'
        ELSE 'Churned (90+ days)'
    END as churn_risk_category,
    COUNT(*) as customer_count,
    ROUND(AVG(total_orders), 1) as avg_total_orders,
    ROUND(AVG(total_spent), 2) as avg_total_spent,
    ROUND(AVG(days_since_last_order), 1) as avg_days_since_last_order,
    ROUND(SUM(total_spent), 2) as segment_revenue,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as pct_of_customers
FROM last_orders
GROUP BY 
    CASE 
        WHEN days_since_last_order <= 30 THEN 'Active (0-30 days)'
        WHEN days_since_last_order <= 60 THEN 'At Risk (31-60 days)'
        WHEN days_since_last_order <= 90 THEN 'Churning (61-90 days)'
        ELSE 'Churned (90+ days)'
    END
ORDER BY 
    CASE 
        WHEN churn_risk_category = 'Active (0-30 days)' THEN 1
        WHEN churn_risk_category = 'At Risk (31-60 days)' THEN 2
        WHEN churn_risk_category = 'Churning (61-90 days)' THEN 3
        ELSE 4
    END;

-- 6.3 Market Basket Analysis (Frequently Bought Together)
WITH order_products AS (
    SELECT 
        customer_id,
        order_date,
        STRING_AGG(product_name, ', ' ORDER BY product_name) as products_in_order,
        COUNT(*) as items_in_order,
        SUM(total_value) as order_total
    FROM sales
    GROUP BY customer_id, order_date
    HAVING COUNT(*) > 1  -- Only multi-item orders
)
SELECT 
    items_in_order,
    COUNT(*) as frequency,
    ROUND(AVG(order_total), 2) as avg_order_value,
    STRING_AGG(DISTINCT products_in_order, ' | ') as common_combinations
FROM order_products
GROUP BY items_in_order
HAVING COUNT(*) >= 2
ORDER BY frequency DESC, items_in_order;

-- Create summary view for dashboard
CREATE OR REPLACE VIEW v_business_dashboard AS
SELECT 
    'sales_summary' as metric_category,
    json_build_object(
        'total_orders', (SELECT COUNT(*) FROM sales),
        'total_revenue', (SELECT SUM(total_value) FROM sales),
        'avg_order_value', (SELECT ROUND(AVG(total_value), 2) FROM sales),
        'unique_customers', (SELECT COUNT(DISTINCT customer_id) FROM sales),
        'unique_products', (SELECT COUNT(DISTINCT product_name) FROM sales)
    ) as metrics
UNION ALL
SELECT 
    'top_categories' as metric_category,
    json_agg(json_build_object('category', category, 'revenue', total_revenue))
FROM (
    SELECT category, SUM(total_value) as total_revenue 
    FROM sales 
    GROUP BY category 
    ORDER BY total_revenue DESC 
    LIMIT 5
) top_cats
UNION ALL
SELECT 
    'monthly_trend' as metric_category,
    json_agg(json_build_object('month', month, 'revenue', monthly_revenue))
FROM (
    SELECT 
        TO_CHAR(DATE_TRUNC('month', order_date), 'YYYY-MM') as month,
        SUM(total_value) as monthly_revenue
    FROM sales
    GROUP BY DATE_TRUNC('month', order_date)
    ORDER BY month
) monthly_data;

-- Export results for visualization
\copy (SELECT * FROM v_business_dashboard) TO 'dashboard_data.json' CSV HEADER;

PRINT 'Advanced analytics queries completed successfully!';
PRINT 'Results exported for visualization and reporting.';