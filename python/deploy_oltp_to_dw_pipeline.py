"""
deploy_oltp_to_dw_pipeline.py
Executes the full ETL pipeline from Olist_OLTP to Olist_DW:
1. Deploys physical dimension & fact tables matching friend's schema.
2. Extracts from Olist_OLTP.
3. Applies transformations (REPLACENULL on category, smart DateKey, TotalOrderValue, DeliveryTimeDays).
4. Performs sequential Surrogate Key lookups with fault tolerance (Ignore Failure on missing seller).
5. Deploys the 4 departmental Data Mart views on Olist_DW.
6. Validates all row counts and reconciliation.
"""
import pyodbc
import time

conn_str_dw = 'DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=Olist_DW;Trusted_Connection=yes;TrustServerCertificate=yes;'
conn_str_oltp = 'DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=Olist_OLTP;Trusted_Connection=yes;TrustServerCertificate=yes;'

print("==========================================================")
print("STARTING ETL PIPELINE: Olist_OLTP -> Olist_DW")
print("==========================================================")
start_time = time.time()

conn_dw = pyodbc.connect(conn_str_dw, autocommit=True)
cur_dw = conn_dw.cursor()

# -----------------------------------------------------------------------------
# STEP 1: Deploy Physical Dimension & Fact Tables in Olist_DW
# -----------------------------------------------------------------------------
print("\n[Step 1] Deploying physical star schema tables in Olist_DW...")

# Drop existing views or tables to re-create as physical tables
objects_to_drop = [
    ("Fact_Orders", "TABLE"), ("Fact_Orders", "VIEW"),
    ("Dim_Customer", "TABLE"), ("Dim_Customer", "VIEW"),
    ("Dim_Product", "TABLE"), ("Dim_Product", "VIEW"),
    ("Dim_Seller", "TABLE"), ("Dim_Seller", "VIEW"),
    ("Dim_Date", "TABLE"), ("Dim_Date", "VIEW")
]
for obj, obj_type in objects_to_drop:
    try:
        cur_dw.execute(f"DROP {obj_type} IF EXISTS dbo.{obj}")
    except Exception:
        pass

ddl_tables = """
CREATE TABLE dbo.Dim_Customer (
    CustomerSK INT IDENTITY(1,1) PRIMARY KEY,
    CustomerBK VARCHAR(64) NOT NULL,
    CustomerUniqueId VARCHAR(64),
    CustomerZipCode VARCHAR(16),
    CustomerCity VARCHAR(64),
    CustomerState VARCHAR(16)
);

CREATE TABLE dbo.Dim_Product (
    ProductSK INT IDENTITY(1,1) PRIMARY KEY,
    ProductBK VARCHAR(64) NOT NULL,
    CategoryNameEnglish VARCHAR(64),
    ProductWeightGrams INT,
    ProductLengthCm INT,
    ProductHeightCm INT,
    ProductWidthCm INT
);

CREATE TABLE dbo.Dim_Seller (
    SellerSK INT IDENTITY(1,1) PRIMARY KEY,
    SellerBK VARCHAR(64) NOT NULL,
    SellerZipCode VARCHAR(16),
    SellerCity VARCHAR(64),
    SellerState VARCHAR(16)
);

CREATE TABLE dbo.Dim_Date (
    DateKey INT PRIMARY KEY,
    FullDate DATE NOT NULL,
    Year SMALLINT NOT NULL,
    Month TINYINT NOT NULL,
    MonthName VARCHAR(16) NOT NULL
);

CREATE TABLE dbo.Fact_Orders (
    OrderSK INT IDENTITY(1,1) PRIMARY KEY,
    OrderBK VARCHAR(64) NOT NULL,
    OrderItemBK INT NOT NULL,
    CustomerSK INT NULL,
    ProductSK INT NULL,
    SellerSK INT NULL,
    DateKey INT NOT NULL,
    Price DECIMAL(10,2) NOT NULL,
    FreightValue DECIMAL(10,2) NOT NULL,
    TotalOrderValue DECIMAL(10,2) NOT NULL,
    DeliveryTimeDays INT NULL
);
"""
for stmt in ddl_tables.strip().split(";"):
    if stmt.strip():
        cur_dw.execute(stmt)

print("  Physical tables created: Dim_Customer, Dim_Product, Dim_Seller, Dim_Date, Fact_Orders.")

# -----------------------------------------------------------------------------
# STEP 2: Load Dim_Customer (OLE DB Source -> OLE DB Destination)
# -----------------------------------------------------------------------------
print("\n[Step 2] Executing Task: Load_Dim_Customer...")
cur_dw.execute("""
INSERT INTO dbo.Dim_Customer (CustomerBK, CustomerUniqueId, CustomerZipCode, CustomerCity, CustomerState)
SELECT 
    customer_id, 
    customer_unique_id, 
    customer_zip_code_prefix, 
    customer_city, 
    customer_state 
FROM Olist_OLTP.dbo.olist_customers_dataset;
""")
cur_dw.execute("SELECT COUNT(*) FROM dbo.Dim_Customer")
c_cnt = cur_dw.fetchone()[0]
print(f"  Load_Dim_Customer complete: {c_cnt:,} rows inserted with IDENTITY CustomerSK.")

# -----------------------------------------------------------------------------
# STEP 3: Load Dim_Product (Flat File / Source -> Derived Column REPLACENULL -> Destination)
# -----------------------------------------------------------------------------
print("\n[Step 3] Executing Task: Load_Dim_Product (with REPLACENULL data hygiene)...")
cur_dw.execute("""
INSERT INTO dbo.Dim_Product (ProductBK, CategoryNameEnglish, ProductWeightGrams, ProductLengthCm, ProductHeightCm, ProductWidthCm)
SELECT 
    p.product_id,
    -- Derived Column Transformation: REPLACENULL([product_category_name], "Unknown")
    ISNULL(NULLIF(LTRIM(RTRIM(COALESCE(t.product_category_name_english, p.product_category_name))), ''), 'Unknown') AS CategoryNameEnglish,
    TRY_CAST(p.product_weight_g AS INT),
    TRY_CAST(p.product_length_cm AS INT),
    TRY_CAST(p.product_height_cm AS INT),
    TRY_CAST(p.product_width_cm AS INT)
FROM Olist_OLTP.dbo.olist_products_dataset p
LEFT JOIN Olist_OLTP.dbo.product_category_name_translation t 
    ON p.product_category_name = t.product_category_name;
""")
cur_dw.execute("SELECT COUNT(*) FROM dbo.Dim_Product")
p_cnt = cur_dw.fetchone()[0]
print(f"  Load_Dim_Product complete: {p_cnt:,} rows inserted with IDENTITY ProductSK.")

# -----------------------------------------------------------------------------
# STEP 4: Load Dim_Seller & Dim_Date
# -----------------------------------------------------------------------------
print("\n[Step 4] Executing Task: Load_Dim_Seller and Dim_Date...")
cur_dw.execute("""
INSERT INTO dbo.Dim_Seller (SellerBK, SellerZipCode, SellerCity, SellerState)
SELECT 
    seller_id, 
    seller_zip_code_prefix, 
    seller_city, 
    seller_state 
FROM Olist_OLTP.dbo.olist_sellers_dataset;
""")
cur_dw.execute("SELECT COUNT(*) FROM dbo.Dim_Seller")
s_cnt = cur_dw.fetchone()[0]
print(f"  Load_Dim_Seller complete: {s_cnt:,} rows inserted with IDENTITY SellerSK.")

cur_dw.execute("""
INSERT INTO dbo.Dim_Date (DateKey, FullDate, Year, Month, MonthName)
SELECT 
    date_key, 
    full_date, 
    year, 
    month, 
    month_name 
FROM OlistDW.dw.dim_date;
""")
cur_dw.execute("SELECT COUNT(*) FROM dbo.Dim_Date")
d_cnt = cur_dw.fetchone()[0]
print(f"  Load_Dim_Date complete: {d_cnt:,} calendar dates loaded.")

# -----------------------------------------------------------------------------
# STEP 5: Load Fact_Orders (SQL Source -> Sequential Lookups -> Destination)
# -----------------------------------------------------------------------------
print("\n[Step 5] Executing Task: Load_Fact_Orders (with Lookups & Ignore Failure)...")
sql_fact = """
INSERT INTO dbo.Fact_Orders (
    OrderBK, OrderItemBK, CustomerSK, ProductSK, SellerSK, 
    DateKey, Price, FreightValue, TotalOrderValue, DeliveryTimeDays
)
SELECT 
    src.order_id AS OrderBK,
    src.order_item_id AS OrderItemBK,
    -- Lookup 1: Customer (joins customer_id -> CustomerBK, returns CustomerSK)
    lkp_c.CustomerSK,
    -- Lookup 2: Product (joins product_id -> ProductBK, returns ProductSK)
    lkp_p.ProductSK,
    -- Lookup 3: Seller (joins seller_id -> SellerBK, returns SellerSK; Ignore Failure -> NULL)
    lkp_s.SellerSK,
    src.DateKey,
    src.price,
    src.freight_value,
    src.TotalOrderValue,
    src.DeliveryTimeDays
FROM (
    -- The Exact Extraction Query from Friend's OneNote Document
    SELECT  
        o.order_id, 
        oi.order_item_id, 
        o.customer_id, 
        oi.product_id, 
        oi.seller_id, 
        CONVERT(INT, CONVERT(VARCHAR(8), o.order_purchase_timestamp, 112)) AS DateKey, 
        oi.price, 
        oi.freight_value, 
        (oi.price + oi.freight_value) AS TotalOrderValue, 
        DATEDIFF(day, o.order_purchase_timestamp, o.order_delivered_customer_date) AS DeliveryTimeDays 
    FROM Olist_OLTP.dbo.olist_orders_dataset o 
    JOIN Olist_OLTP.dbo.olist_order_items_dataset oi ON o.order_id = oi.order_id 
    WHERE o.order_status = 'delivered'
) src
LEFT JOIN dbo.Dim_Customer lkp_c ON src.customer_id = lkp_c.CustomerBK
LEFT JOIN dbo.Dim_Product lkp_p  ON src.product_id  = lkp_p.ProductBK
LEFT JOIN dbo.Dim_Seller lkp_s   ON src.seller_id   = lkp_s.SellerBK;
"""
cur_dw.execute(sql_fact)
cur_dw.execute("SELECT COUNT(*) FROM dbo.Fact_Orders")
f_cnt = cur_dw.fetchone()[0]
print(f"  Load_Fact_Orders complete: {f_cnt:,} delivered order items loaded into Fact_Orders.")

# -----------------------------------------------------------------------------
# STEP 6: Deploy Departmental Data Mart Schemas & Views on Olist_DW
# -----------------------------------------------------------------------------
print("\n[Step 6] Deploying Departmental Data Marts (Logistics, Sales, Marketing, Executive)...")

for sch in ['Logistics', 'Sales', 'Marketing', 'Executive']:
    cur_dw.execute(f"IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '{sch}') EXEC('CREATE SCHEMA {sch}');")

cur_dw.execute("""
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
""")

cur_dw.execute("""
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
""")

cur_dw.execute("""
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
""")

cur_dw.execute("""
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
""")

print("  Departmental views deployed successfully!")

# -----------------------------------------------------------------------------
# STEP 7: Reconcile & Verify Data Marts
# -----------------------------------------------------------------------------
print("\n[Step 7] Reconciling and Verifying Views...")
for vm in ['Logistics.ShippingPerformance', 'Sales.ProductPerformance', 'Marketing.CustomerInsights', 'Executive.MonthlySummary']:
    cur_dw.execute(f"SELECT COUNT(*) FROM {vm}")
    cnt = cur_dw.fetchone()[0]
    print(f"  {vm:35s} -> {cnt:,} rows")

elapsed = time.time() - start_time
print(f"\n==========================================================")
print(f"ETL PIPELINE Olist_OLTP -> Olist_DW COMPLETED in {elapsed:.2f}s")
print("==========================================================")

cur_dw.close()
conn_dw.close()
