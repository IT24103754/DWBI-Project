"""
Creates the Olist_OLTP database and populates its tables/views from OlistDW.stg.*
Matching the exact source database structure from the friend's SSIS document.
"""
import pyodbc

conn_master = pyodbc.connect(
    'DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=master;Trusted_Connection=yes;TrustServerCertificate=yes;',
    autocommit=True
)
cur_master = conn_master.cursor()

# 1. Create Olist_OLTP database if not exists
cur_master.execute("SELECT name FROM sys.databases WHERE name = 'Olist_OLTP'")
if not cur_master.fetchone():
    print("Creating database Olist_OLTP...")
    cur_master.execute("CREATE DATABASE Olist_OLTP;")
    print("Database Olist_OLTP created successfully!")
else:
    print("Database Olist_OLTP already exists.")

# 2. Create Olist_DW database if not exists (for compatibility with friend's name)
cur_master.execute("SELECT name FROM sys.databases WHERE name = 'Olist_DW'")
if not cur_master.fetchone():
    print("Creating database Olist_DW...")
    cur_master.execute("CREATE DATABASE Olist_DW;")
    print("Database Olist_DW created successfully!")
else:
    print("Database Olist_DW already exists.")

cur_master.close()
conn_master.close()

# 3. Connect to Olist_OLTP and create all standard Olist tables / views
conn_oltp = pyodbc.connect(
    'DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=Olist_OLTP;Trusted_Connection=yes;TrustServerCertificate=yes;',
    autocommit=True
)
cur_oltp = conn_oltp.cursor()

tables_to_create = [
    ("olist_customers_dataset", """
        SELECT customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state 
        FROM OlistDW.stg.customers
    """),
    ("olist_orders_dataset", """
        SELECT order_id, customer_id, order_status, order_purchase_timestamp, order_approved_at, 
               order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date 
        FROM OlistDW.stg.orders
    """),
    ("olist_order_items_dataset", """
        SELECT order_id, order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value 
        FROM OlistDW.stg.order_items
    """),
    ("olist_products_dataset", """
        SELECT product_id, product_category_name, product_name_lenght, product_description_lenght, 
               product_photos_qty, product_weight_g, product_length_cm, product_height_cm, product_width_cm 
        FROM OlistDW.stg.products
    """),
    ("olist_sellers_dataset", """
        SELECT seller_id, seller_zip_code_prefix, seller_city, seller_state 
        FROM OlistDW.stg.sellers
    """),
    ("olist_order_payments_dataset", """
        SELECT order_id, payment_sequential, payment_type, payment_installments, payment_value 
        FROM OlistDW.stg.order_payments
    """),
    ("olist_order_reviews_dataset", """
        SELECT review_id, order_id, review_score, review_comment_title, review_comment_message, 
               review_creation_date, review_answer_timestamp 
        FROM OlistDW.stg.order_reviews
    """),
    ("olist_geolocation_dataset", """
        SELECT geolocation_zip_code_prefix, geolocation_lat, geolocation_lng, geolocation_city, geolocation_state 
        FROM OlistDW.stg.geolocation
    """),
    ("product_category_name_translation", """
        SELECT product_category_name, product_category_name_english 
        FROM OlistDW.stg.product_category
    """)
]

for name, query in tables_to_create:
    cur_oltp.execute(f"CREATE OR ALTER VIEW dbo.{name} AS {query};")
    cur_oltp.execute(f"SELECT COUNT(*) FROM dbo.{name}")
    count = cur_oltp.fetchone()[0]
    print(f"Olist_OLTP.dbo.{name:35s} -> {count:,} rows")

cur_oltp.close()
conn_oltp.close()

# 4. Connect to Olist_DW and create compatibility views
conn_dw = pyodbc.connect(
    'DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=Olist_DW;Trusted_Connection=yes;TrustServerCertificate=yes;',
    autocommit=True
)
cur_dw = conn_dw.cursor()

dw_views = [
    ("Dim_Customer", """
        SELECT customer_key AS CustomerSK, customer_id AS CustomerBK, customer_id AS CustomerUniqueId, 
               zip_prefix AS CustomerZipCode, city AS CustomerCity, state AS CustomerState 
        FROM OlistDW.dw.dim_customer
    """),
    ("Dim_Product", """
        SELECT product_key AS ProductSK, product_id AS ProductBK, category_en AS CategoryNameEnglish, 
               weight_g AS ProductWeightGrams, length_cm AS ProductLengthCm, height_cm AS ProductHeightCm, width_cm AS ProductWidthCm 
        FROM OlistDW.dw.dim_product
    """),
    ("Dim_Seller", """
        SELECT seller_key AS SellerSK, seller_id AS SellerBK, zip_prefix AS SellerZipCode, 
               city AS SellerCity, state AS SellerState 
        FROM OlistDW.dw.dim_seller
    """),
    ("Dim_Date", """
        SELECT date_key AS DateKey, full_date AS FullDate, year AS Year, month AS Month, month_name AS MonthName 
        FROM OlistDW.dw.dim_date
    """),
    ("Fact_Orders", """
        SELECT order_id AS OrderBK, order_item_id AS OrderItemBK, customer_key AS CustomerSK, product_key AS ProductSK, 
               seller_key AS SellerSK, date_key AS DateKey, price_usd AS Price, freight_value AS FreightValue, 
               (price_usd + freight_value) AS TotalOrderValue, delivery_delay_days AS DeliveryTimeDays 
        FROM OlistDW.dw.fact_order_items
    """)
]

for name, query in dw_views:
    cur_dw.execute(f"CREATE OR ALTER VIEW dbo.{name} AS {query};")
    cur_dw.execute(f"SELECT COUNT(*) FROM dbo.{name}")
    count = cur_dw.fetchone()[0]
    print(f"Olist_DW.dbo.{name:35s} -> {count:,} rows")

cur_dw.close()
conn_dw.close()

print("\nAll databases and views successfully deployed!")
