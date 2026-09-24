-- ============================================================
-- IT3101 DWBI Project – Olist Brazilian E-Commerce
-- Script 01: Staging Schema (SQL Server 2025)
-- All 9 CSV files loaded into [olist_staging] schema
-- ============================================================

USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'OlistDW')
BEGIN
    CREATE DATABASE OlistDW;
END
GO

USE OlistDW;
GO

-- ============================================================
-- Create schemas
-- ============================================================
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'stg')
    EXEC('CREATE SCHEMA stg');
GO
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'dw')
    EXEC('CREATE SCHEMA dw');
GO

-- ============================================================
-- Drop existing staging tables (clean load)
-- ============================================================
IF OBJECT_ID('stg.exchange_rates',      'U') IS NOT NULL DROP TABLE stg.exchange_rates;
IF OBJECT_ID('stg.order_reviews',       'U') IS NOT NULL DROP TABLE stg.order_reviews;
IF OBJECT_ID('stg.order_payments',      'U') IS NOT NULL DROP TABLE stg.order_payments;
IF OBJECT_ID('stg.geolocation',         'U') IS NOT NULL DROP TABLE stg.geolocation;
IF OBJECT_ID('stg.order_items',         'U') IS NOT NULL DROP TABLE stg.order_items;
IF OBJECT_ID('stg.orders',              'U') IS NOT NULL DROP TABLE stg.orders;
IF OBJECT_ID('stg.sellers',             'U') IS NOT NULL DROP TABLE stg.sellers;
IF OBJECT_ID('stg.products',            'U') IS NOT NULL DROP TABLE stg.products;
IF OBJECT_ID('stg.product_category',    'U') IS NOT NULL DROP TABLE stg.product_category;
IF OBJECT_ID('stg.customers',           'U') IS NOT NULL DROP TABLE stg.customers;
GO

-- ============================================================
-- 1. stg.customers  (olist_customers_dataset.csv)
-- ============================================================
CREATE TABLE stg.customers (
    customer_id              VARCHAR(50) NOT NULL,
    customer_unique_id       VARCHAR(50),
    customer_zip_code_prefix VARCHAR(10),
    customer_city            VARCHAR(100),
    customer_state           VARCHAR(5),
    stg_load_dt              DATETIME DEFAULT GETDATE()
);
GO

-- ============================================================
-- 2. stg.products  (olist_products_dataset.csv)
-- ============================================================
CREATE TABLE stg.products (
    product_id                   VARCHAR(50) NOT NULL,
    product_category_name        VARCHAR(100),
    product_name_lenght          INT,            -- intentional typo matches source
    product_description_lenght   INT,
    product_photos_qty           INT,
    product_weight_g             INT,
    product_length_cm            INT,
    product_height_cm            INT,
    product_width_cm             INT,
    stg_load_dt                  DATETIME DEFAULT GETDATE()
);
GO

-- ============================================================
-- 3. stg.product_category  (product_category_name_translation.csv)
-- ============================================================
CREATE TABLE stg.product_category (
    product_category_name         VARCHAR(100),
    product_category_name_english VARCHAR(100),
    stg_load_dt                   DATETIME DEFAULT GETDATE()
);
GO

-- ============================================================
-- 4. stg.sellers  (olist_sellers_dataset.csv)
-- ============================================================
CREATE TABLE stg.sellers (
    seller_id              VARCHAR(50) NOT NULL,
    seller_zip_code_prefix VARCHAR(10),
    seller_city            VARCHAR(100),
    seller_state           VARCHAR(5),
    stg_load_dt            DATETIME DEFAULT GETDATE()
);
GO

-- ============================================================
-- 5. stg.orders  (olist_orders_dataset.csv)
-- ============================================================
CREATE TABLE stg.orders (
    order_id                     VARCHAR(50) NOT NULL,
    customer_id                  VARCHAR(50),
    order_status                 VARCHAR(20),
    order_purchase_timestamp     DATETIME,
    order_approved_at            DATETIME,
    order_delivered_carrier_date DATETIME,
    order_delivered_customer_date DATETIME,
    order_estimated_delivery_date DATETIME,
    stg_load_dt                  DATETIME DEFAULT GETDATE()
);
GO

-- ============================================================
-- 6. stg.order_items  (olist_order_items_dataset.csv)
-- ============================================================
CREATE TABLE stg.order_items (
    order_id            VARCHAR(50) NOT NULL,
    order_item_id       INT         NOT NULL,
    product_id          VARCHAR(50),
    seller_id           VARCHAR(50),
    shipping_limit_date DATETIME,
    price               DECIMAL(10,2),
    freight_value       DECIMAL(10,2),
    stg_load_dt         DATETIME DEFAULT GETDATE()
);
GO

-- ============================================================
-- 7. stg.order_payments  (olist_order_payments_dataset.csv)
-- ============================================================
CREATE TABLE stg.order_payments (
    order_id             VARCHAR(50) NOT NULL,
    payment_sequential   INT,
    payment_type         VARCHAR(30),
    payment_installments INT,
    payment_value        DECIMAL(10,2),
    stg_load_dt          DATETIME DEFAULT GETDATE()
);
GO

-- ============================================================
-- 8. stg.order_reviews  (olist_order_reviews_dataset.csv)
-- ============================================================
CREATE TABLE stg.order_reviews (
    review_id                VARCHAR(50),
    order_id                 VARCHAR(50),
    review_score             TINYINT,
    review_comment_title     NVARCHAR(100),
    review_comment_message   NVARCHAR(MAX),
    review_creation_date     DATETIME,
    review_answer_timestamp  DATETIME,
    stg_load_dt              DATETIME DEFAULT GETDATE()
);
GO

-- ============================================================
-- 9. stg.geolocation  (olist_geolocation_dataset.csv)
-- ============================================================
CREATE TABLE stg.geolocation (
    geolocation_zip_code_prefix VARCHAR(10),
    geolocation_lat             DECIMAL(9,6),
    geolocation_lng             DECIMAL(9,6),
    geolocation_city            VARCHAR(100),
    geolocation_state           VARCHAR(5),
    stg_load_dt                 DATETIME DEFAULT GETDATE()
);
GO

-- ============================================================
-- 10. stg.exchange_rates  (populated via Python/API)
-- ============================================================
CREATE TABLE stg.exchange_rates (
    rate_date    DATE        NOT NULL,
    brl_per_usd  DECIMAL(10,6),
    usd_per_brl  DECIMAL(10,6),
    stg_load_dt  DATETIME DEFAULT GETDATE(),
    CONSTRAINT PK_stg_exchange_rates PRIMARY KEY (rate_date)
);
GO

-- ============================================================
-- ETL Run Log (shared with dw schema)
-- ============================================================
IF OBJECT_ID('dw.etl_run_log', 'U') IS NULL
BEGIN
    CREATE TABLE dw.etl_run_log (
        run_id       INT IDENTITY PRIMARY KEY,
        package_name VARCHAR(100),
        rows_loaded  INT,
        start_time   DATETIME DEFAULT GETDATE(),
        end_time     DATETIME,
        status       VARCHAR(20) DEFAULT 'RUNNING',
        error_msg    NVARCHAR(MAX)
    );
END
GO

PRINT 'Staging schema created successfully in OlistDW.';
GO
