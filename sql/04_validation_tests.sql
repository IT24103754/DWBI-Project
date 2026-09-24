-- ============================================================
-- IT3101 DWBI Project – Olist Brazilian E-Commerce
-- Script 04: ETL Validation Tests
-- Run AFTER full ETL to verify data quality
-- ============================================================

USE OlistDW;
GO

PRINT '============================================================';
PRINT 'VALIDATION SUITE – Olist DWBI ETL';
PRINT CONVERT(VARCHAR, GETDATE(), 121);
PRINT '============================================================';

-- ============================================================
-- TEST 1: Row counts – staging vs source CSV (expected counts)
-- ============================================================
PRINT '';
PRINT '-- TEST 1: Staging row counts';
SELECT 'stg.customers'     AS staging_table, COUNT(*) AS rows_loaded, 99441   AS expected FROM stg.customers
UNION ALL
SELECT 'stg.orders',                          COUNT(*),              99441             FROM stg.orders
UNION ALL
SELECT 'stg.order_items',                     COUNT(*),              112650            FROM stg.order_items
UNION ALL
SELECT 'stg.order_payments',                  COUNT(*),              103886            FROM stg.order_payments
UNION ALL
SELECT 'stg.order_reviews',                   COUNT(*),              99224             FROM stg.order_reviews
UNION ALL
SELECT 'stg.products',                        COUNT(*),              32951             FROM stg.products
UNION ALL
SELECT 'stg.sellers',                         COUNT(*),              3095              FROM stg.sellers
UNION ALL
SELECT 'stg.geolocation',                     COUNT(*),              1000163           FROM stg.geolocation
UNION ALL
SELECT 'stg.product_category',                COUNT(*),              71                FROM stg.product_category;
GO

-- ============================================================
-- TEST 2: Dimension row counts
-- ============================================================
PRINT '';
PRINT '-- TEST 2: Dimension table row counts';
SELECT 'dw.dim_customer'  AS dim_table, COUNT(*) AS rows FROM dw.dim_customer
UNION ALL
SELECT 'dw.dim_product',                COUNT(*)        FROM dw.dim_product
UNION ALL
SELECT 'dw.dim_seller',                 COUNT(*)        FROM dw.dim_seller
UNION ALL
SELECT 'dw.dim_date',                   COUNT(*)        FROM dw.dim_date
UNION ALL
SELECT 'dw.dim_geography',              COUNT(*)        FROM dw.dim_geography;
GO

-- ============================================================
-- TEST 3: Fact table row count
-- ============================================================
PRINT '';
PRINT '-- TEST 3: Fact table row count';
SELECT COUNT(*)         AS fact_rows,
       COUNT(DISTINCT order_id) AS distinct_orders
FROM dw.fact_order_items;
GO

-- ============================================================
-- TEST 4: Referential integrity – orphaned fact keys
-- ============================================================
PRINT '';
PRINT '-- TEST 4: Orphaned keys in fact (should all be 0)';
SELECT
    SUM(CASE WHEN c.customer_key IS NULL THEN 1 ELSE 0 END) AS orphan_customer,
    SUM(CASE WHEN p.product_key  IS NULL THEN 1 ELSE 0 END) AS orphan_product,
    SUM(CASE WHEN s.seller_key   IS NULL THEN 1 ELSE 0 END) AS orphan_seller,
    SUM(CASE WHEN d.date_key     IS NULL THEN 1 ELSE 0 END) AS orphan_date
FROM dw.fact_order_items f
LEFT JOIN dw.dim_customer c ON f.customer_key = c.customer_key
LEFT JOIN dw.dim_product  p ON f.product_key  = p.product_key
LEFT JOIN dw.dim_seller   s ON f.seller_key   = s.seller_key
LEFT JOIN dw.dim_date     d ON f.date_key     = d.date_key;
GO

-- ============================================================
-- TEST 5: Null measures check
-- ============================================================
PRINT '';
PRINT '-- TEST 5: NULL measures in fact table';
SELECT
    SUM(CASE WHEN price_brl       IS NULL THEN 1 ELSE 0 END) AS null_price_brl,
    SUM(CASE WHEN freight_value   IS NULL THEN 1 ELSE 0 END) AS null_freight,
    SUM(CASE WHEN price_usd       IS NULL THEN 1 ELSE 0 END) AS null_price_usd,
    SUM(CASE WHEN delivery_delay_days IS NULL THEN 1 ELSE 0 END) AS null_delay
FROM dw.fact_order_items;
GO

-- ============================================================
-- TEST 6: ETL run log – row count reconciliation
-- ============================================================
PRINT '';
PRINT '-- TEST 6: ETL run log';
SELECT package_name, rows_loaded, start_time, end_time, status
FROM dw.etl_run_log
ORDER BY run_id;
GO

-- ============================================================
-- TEST 7: Review score distribution (sanity check 1-5)
-- ============================================================
PRINT '';
PRINT '-- TEST 7: Review score distribution';
SELECT review_score, COUNT(*) AS cnt
FROM dw.fact_order_items
WHERE review_score IS NOT NULL
GROUP BY review_score
ORDER BY review_score;
GO

-- ============================================================
-- TEST 8: Delivery delay distribution
-- ============================================================
PRINT '';
PRINT '-- TEST 8: Delivery delay summary';
SELECT
    MIN(delivery_delay_days)  AS min_delay,
    MAX(delivery_delay_days)  AS max_delay,
    AVG(CAST(delivery_delay_days AS FLOAT)) AS avg_delay,
    SUM(CASE WHEN delivery_delay_days > 0 THEN 1 ELSE 0 END)  AS late_count,
    SUM(CASE WHEN delivery_delay_days <= 0 THEN 1 ELSE 0 END) AS on_time_count
FROM dw.fact_order_items
WHERE delivery_delay_days IS NOT NULL;
GO

-- ============================================================
-- TEST 9: Exchange rate coverage
-- ============================================================
PRINT '';
PRINT '-- TEST 9: Exchange rate date coverage';
SELECT
    MIN(rate_date)  AS earliest_rate,
    MAX(rate_date)  AS latest_rate,
    COUNT(*)        AS rate_rows
FROM stg.exchange_rates;
GO

-- ============================================================
-- TEST 10: Top 10 states by revenue
-- ============================================================
PRINT '';
PRINT '-- TEST 10: Top 10 customer states by revenue';
SELECT TOP 10
    c.state,
    COUNT(*)            AS order_items,
    SUM(f.price_brl)    AS revenue_brl
FROM dw.fact_order_items f
JOIN dw.dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.state
ORDER BY revenue_brl DESC;
GO

PRINT '';
PRINT '============================================================';
PRINT 'VALIDATION COMPLETE';
PRINT '============================================================';
