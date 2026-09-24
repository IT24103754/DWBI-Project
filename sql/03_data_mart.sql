-- ============================================================
-- IT3101 DWBI Project – Olist Brazilian E-Commerce
-- Script 03: Data Mart
-- logistics_performance_mart — operations/logistics focused view
-- ============================================================

USE OlistDW;
GO

-- ============================================================
-- Drop if exists
-- ============================================================
IF OBJECT_ID('dw.logistics_performance_mart', 'V') IS NOT NULL
    DROP VIEW dw.logistics_performance_mart;
GO

-- ============================================================
-- Logistics Performance Data Mart (View)
-- Purpose: Pre-aggregated delivery & freight analytics
-- Target users: Operations / Logistics managers
-- ============================================================
CREATE VIEW dw.logistics_performance_mart AS
SELECT
    s.state                                     AS seller_state,
    c.state                                     AS customer_state,
    d.year,
    d.month,
    d.month_name,
    COUNT(*)                                    AS order_item_count,
    COUNT(DISTINCT f.order_id)                  AS distinct_order_count,
    AVG(CAST(f.delivery_delay_days AS FLOAT))   AS avg_delay_days,
    MAX(f.delivery_delay_days)                  AS max_delay_days,
    SUM(CASE WHEN f.delivery_delay_days > 0 THEN 1 ELSE 0 END) AS late_deliveries,
    SUM(CASE WHEN f.delivery_delay_days <= 0 THEN 1 ELSE 0 END) AS on_time_deliveries,
    AVG(f.freight_value)                        AS avg_freight_brl,
    SUM(f.freight_value)                        AS total_freight_brl,
    AVG(CAST(f.review_score AS FLOAT))          AS avg_review_score,
    SUM(f.price_brl)                            AS total_revenue_brl,
    SUM(f.price_usd)                            AS total_revenue_usd
FROM dw.fact_order_items f
JOIN dw.dim_seller   s ON f.seller_key   = s.seller_key
JOIN dw.dim_customer c ON f.customer_key = c.customer_key
JOIN dw.dim_date     d ON f.date_key     = d.date_key
GROUP BY
    s.state, c.state, d.year, d.month, d.month_name;
GO

-- ============================================================
-- Sales Performance Data Mart (View)
-- Purpose: Product / category revenue analytics
-- Target users: Sales / Product managers
-- ============================================================
IF OBJECT_ID('dw.sales_performance_mart', 'V') IS NOT NULL
    DROP VIEW dw.sales_performance_mart;
GO

CREATE VIEW dw.sales_performance_mart AS
SELECT
    p.category_en                               AS product_category,
    d.year,
    d.quarter,
    d.month,
    COUNT(*)                                    AS order_item_count,
    COUNT(DISTINCT f.order_id)                  AS distinct_order_count,
    SUM(f.price_brl)                            AS total_revenue_brl,
    SUM(f.price_usd)                            AS total_revenue_usd,
    AVG(f.price_brl)                            AS avg_order_value_brl,
    AVG(CAST(f.review_score AS FLOAT))          AS avg_review_score,
    SUM(f.freight_value)                        AS total_freight_brl
FROM dw.fact_order_items f
JOIN dw.dim_product  p ON f.product_key  = p.product_key
JOIN dw.dim_date     d ON f.date_key     = d.date_key
GROUP BY
    p.category_en, d.year, d.quarter, d.month;
GO

PRINT 'Data mart views created: dw.logistics_performance_mart, dw.sales_performance_mart';
GO
