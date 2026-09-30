-- ==============================================================================
-- IT3101 - Data Warehousing & Business Intelligence
-- Departmental Data Mart Views (Logistics, Sales, Marketing, Executive)
-- Modeled per ETL Pipeline Architecture specification
-- ==============================================================================

USE OlistDW;
GO

-- ==============================================================================
-- 1. Create Compatibility dbo Views for Dimensions & Fact (Surrogate Keys & Business Keys)
-- ==============================================================================
IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'Dim_Customer' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    EXEC('CREATE VIEW dbo.Dim_Customer AS
    SELECT 
        customer_key AS CustomerSK,
        customer_id AS CustomerBK,
        customer_id AS CustomerUniqueId,
        zip_prefix AS CustomerZipCode,
        city AS CustomerCity,
        state AS CustomerState
    FROM dw.dim_customer;');
END
GO

IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'Dim_Product' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    EXEC('CREATE VIEW dbo.Dim_Product AS
    SELECT 
        product_key AS ProductSK,
        product_id AS ProductBK,
        category_en AS CategoryNameEnglish,
        weight_g AS ProductWeightGrams,
        length_cm AS ProductLengthCm,
        height_cm AS ProductHeightCm,
        width_cm AS ProductWidthCm
    FROM dw.dim_product;');
END
GO

IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'Dim_Seller' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    EXEC('CREATE VIEW dbo.Dim_Seller AS
    SELECT 
        seller_key AS SellerSK,
        seller_id AS SellerBK,
        zip_prefix AS SellerZipCode,
        city AS SellerCity,
        state AS SellerState
    FROM dw.dim_seller;');
END
GO

IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'Dim_Date' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    EXEC('CREATE VIEW dbo.Dim_Date AS
    SELECT 
        date_key AS DateKey,
        full_date AS FullDate,
        year AS Year,
        month AS Month,
        month_name AS MonthName
    FROM dw.dim_date;');
END
GO

IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'Fact_Orders' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    EXEC('CREATE VIEW dbo.Fact_Orders AS
    SELECT 
        order_id AS OrderBK,
        order_item_id AS OrderItemBK,
        customer_key AS CustomerSK,
        product_key AS ProductSK,
        seller_key AS SellerSK,
        date_key AS DateKey,
        price_usd AS Price,
        freight_value AS FreightValue,
        (price_usd + freight_value) AS TotalOrderValue,
        delivery_delay_days AS DeliveryTimeDays
    FROM dw.fact_order_items;');
END
GO

-- ==============================================================================
-- 2. Create the Dedicated Departmental Schemas
-- ==============================================================================
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'Logistics')
BEGIN
    EXEC('CREATE SCHEMA Logistics;');
END
GO

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'Sales')
BEGIN
    EXEC('CREATE SCHEMA Sales;');
END
GO

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'Marketing')
BEGIN
    EXEC('CREATE SCHEMA Marketing;');
END
GO

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'Executive')
BEGIN
    EXEC('CREATE SCHEMA Executive;');
END
GO

-- ==============================================================================
-- 3. Logistics Data Mart: Shipping & Delivery Performance View
-- ==============================================================================
CREATE OR ALTER VIEW Logistics.ShippingPerformance AS
SELECT
    f.OrderBK,
    d.FullDate AS PurchaseDate,
    c.CustomerCity AS DestinationCity,
    c.CustomerState AS DestinationState,
    s.SellerCity AS OriginCity,
    s.SellerState AS OriginState,
    f.FreightValue,
    f.DeliveryTimeDays
FROM dbo.Fact_Orders f
JOIN dbo.Dim_Date d ON f.DateKey = d.DateKey
JOIN dbo.Dim_Customer c ON f.CustomerSK = c.CustomerSK
JOIN dbo.Dim_Seller s ON f.SellerSK = s.SellerSK;
GO

-- ==============================================================================
-- 4. Sales Data Mart: Product Performance & Category Revenue View
-- ==============================================================================
CREATE OR ALTER VIEW Sales.ProductPerformance AS
SELECT
    p.CategoryNameEnglish,
    p.ProductBK AS ProductID,
    d.FullDate AS SaleDate,
    f.Price,
    f.TotalOrderValue
FROM dbo.Fact_Orders f
JOIN dbo.Dim_Product p ON f.ProductSK = p.ProductSK
JOIN dbo.Dim_Date d ON f.DateKey = d.DateKey;
GO

-- ==============================================================================
-- 5. Marketing Data Mart: Customer Demographics & Seasonality Insights View
-- ==============================================================================
CREATE OR ALTER VIEW Marketing.CustomerInsights AS
SELECT
    c.CustomerBK AS CustomerID,
    c.CustomerCity,
    c.CustomerState,
    d.Year,
    d.MonthName,
    d.FullDate AS OrderDate,
    f.TotalOrderValue
FROM dbo.Fact_Orders f
JOIN dbo.Dim_Customer c ON f.CustomerSK = c.CustomerSK
JOIN dbo.Dim_Date d ON f.DateKey = d.DateKey;
GO

-- ==============================================================================
-- 6. Executive Data Mart: Monthly Aggregated Business Summary View
-- ==============================================================================
CREATE OR ALTER VIEW Executive.MonthlySummary AS
SELECT
    d.Year,
    d.Month,
    d.MonthName,
    COUNT(DISTINCT f.OrderBK) AS TotalOrders,
    SUM(f.TotalOrderValue) AS TotalRevenue,
    SUM(f.FreightValue) AS TotalFreightCosts
FROM dbo.Fact_Orders f
JOIN dbo.Dim_Date d ON f.DateKey = d.DateKey
GROUP BY
    d.Year,
    d.Month,
    d.MonthName;
GO
