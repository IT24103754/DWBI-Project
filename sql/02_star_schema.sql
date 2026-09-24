-- ============================================================
-- IT3101 DWBI Project – Olist Brazilian E-Commerce
-- Script 02: Star Schema (DW layer)
-- Fact + 5 Dimension tables with surrogate keys
-- SCD Type 1 (overwrite) — justified: closed 2016-2018 dataset
-- ============================================================

USE OlistDW;
GO

-- ============================================================
-- Drop fact first (has FK refs), then dims
-- ============================================================
IF OBJECT_ID('dw.fact_order_items',      'U') IS NOT NULL DROP TABLE dw.fact_order_items;
IF OBJECT_ID('dw.dim_geography',         'U') IS NOT NULL DROP TABLE dw.dim_geography;
IF OBJECT_ID('dw.dim_date',              'U') IS NOT NULL DROP TABLE dw.dim_date;
IF OBJECT_ID('dw.dim_seller',            'U') IS NOT NULL DROP TABLE dw.dim_seller;
IF OBJECT_ID('dw.dim_product',           'U') IS NOT NULL DROP TABLE dw.dim_product;
IF OBJECT_ID('dw.dim_customer',          'U') IS NOT NULL DROP TABLE dw.dim_customer;
GO

-- ============================================================
-- DIMENSION 1: dim_customer
-- ============================================================
CREATE TABLE dw.dim_customer (
    customer_key   INT IDENTITY(1,1) PRIMARY KEY,
    customer_id    VARCHAR(50)  NOT NULL,
    city           VARCHAR(100),
    state          VARCHAR(5),
    zip_prefix     VARCHAR(10),
    scd_load_dt    DATETIME DEFAULT GETDATE()
);
CREATE UNIQUE INDEX UQ_dim_customer_id ON dw.dim_customer(customer_id);
GO

-- ============================================================
-- DIMENSION 2: dim_product
-- ============================================================
CREATE TABLE dw.dim_product (
    product_key  INT IDENTITY(1,1) PRIMARY KEY,
    product_id   VARCHAR(50)  NOT NULL,
    category_pt  VARCHAR(100),
    category_en  VARCHAR(100),
    weight_g     INT,
    length_cm    INT,
    height_cm    INT,
    width_cm     INT,
    scd_load_dt  DATETIME DEFAULT GETDATE()
);
CREATE UNIQUE INDEX UQ_dim_product_id ON dw.dim_product(product_id);
GO

-- ============================================================
-- DIMENSION 3: dim_seller
-- ============================================================
CREATE TABLE dw.dim_seller (
    seller_key   INT IDENTITY(1,1) PRIMARY KEY,
    seller_id    VARCHAR(50)  NOT NULL,
    city         VARCHAR(100),
    state        VARCHAR(5),
    zip_prefix   VARCHAR(10),
    scd_load_dt  DATETIME DEFAULT GETDATE()
);
CREATE UNIQUE INDEX UQ_dim_seller_id ON dw.dim_seller(seller_id);
GO

-- ============================================================
-- DIMENSION 4: dim_date  (date_key = YYYYMMDD integer)
-- ============================================================
CREATE TABLE dw.dim_date (
    date_key      INT          PRIMARY KEY,   -- YYYYMMDD
    full_date     DATE         NOT NULL,
    day           TINYINT,
    month         TINYINT,
    month_name    VARCHAR(10),
    quarter       TINYINT,
    year          SMALLINT,
    weekday_num   TINYINT,
    weekday_name  VARCHAR(10),
    is_weekend    BIT
);
GO

-- ============================================================
-- DIMENSION 5: dim_geography
-- ============================================================
CREATE TABLE dw.dim_geography (
    geo_key     INT IDENTITY(1,1) PRIMARY KEY,
    zip_prefix  VARCHAR(10),
    lat         DECIMAL(9,6),
    lng         DECIMAL(9,6),
    city        VARCHAR(100),
    state       VARCHAR(5),
    scd_load_dt DATETIME DEFAULT GETDATE()
);
CREATE UNIQUE INDEX UQ_dim_geography_zip ON dw.dim_geography(zip_prefix);
GO

-- ============================================================
-- FACT TABLE: fact_order_items  (grain = 1 row per order item)
-- ============================================================
CREATE TABLE dw.fact_order_items (
    order_item_key      INT IDENTITY(1,1) PRIMARY KEY,
    -- Natural keys (kept for validation / tracing back to source)
    order_id            VARCHAR(50)  NOT NULL,
    order_item_id       INT          NOT NULL,
    -- Foreign keys to dimensions
    customer_key        INT          NOT NULL REFERENCES dw.dim_customer(customer_key),
    product_key         INT          NOT NULL REFERENCES dw.dim_product(product_key),
    seller_key          INT          NOT NULL REFERENCES dw.dim_seller(seller_key),
    date_key            INT          NOT NULL REFERENCES dw.dim_date(date_key),
    geo_key             INT                   REFERENCES dw.dim_geography(geo_key),
    -- Measures
    price_brl           DECIMAL(10,2),
    price_usd           DECIMAL(10,2),
    freight_value       DECIMAL(10,2),
    review_score        TINYINT,
    delivery_delay_days INT,                  -- negative = early, positive = late
    -- Order context (degenerate dims)
    order_status        VARCHAR(20),
    payment_type        VARCHAR(30),
    payment_value       DECIMAL(10,2),
    etl_load_dt         DATETIME DEFAULT GETDATE(),
    CONSTRAINT UQ_fact_order_item UNIQUE (order_id, order_item_id)
);
GO

-- ============================================================
-- Populate dim_date for 2016-01-01 through 2019-12-31
-- ============================================================
WITH seq AS (
    SELECT TOP (1461)   -- 4 years
        DATEADD(DAY, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) - 1, '2016-01-01') AS dt
    FROM sys.all_objects
)
INSERT INTO dw.dim_date
    (date_key, full_date, day, month, month_name, quarter, year, weekday_num, weekday_name, is_weekend)
SELECT
    CONVERT(INT, FORMAT(dt,'yyyyMMdd')),
    dt,
    DAY(dt),
    MONTH(dt),
    DATENAME(MONTH, dt),
    DATEPART(QUARTER, dt),
    YEAR(dt),
    DATEPART(WEEKDAY, dt),
    DATENAME(WEEKDAY, dt),
    CASE WHEN DATEPART(WEEKDAY, dt) IN (1,7) THEN 1 ELSE 0 END
FROM seq;
GO

PRINT 'Star schema + dim_date populated in OlistDW.dw.*';
GO
