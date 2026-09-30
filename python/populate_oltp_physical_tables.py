"""
populate_oltp_physical_tables.py
Creates physical base tables in Olist_OLTP populated with the raw datasets.
"""
import pyodbc
import time

conn_str_oltp = 'DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=Olist_OLTP;Trusted_Connection=yes;TrustServerCertificate=yes;'
conn_oltp = pyodbc.connect(conn_str_oltp, autocommit=True)
cur = conn_oltp.cursor()

tables = [
    ("olist_customers_dataset", "SELECT customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state FROM OlistDW.stg.customers"),
    ("olist_orders_dataset", "SELECT order_id, customer_id, order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date FROM OlistDW.stg.orders"),
    ("olist_order_items_dataset", "SELECT order_id, order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value FROM OlistDW.stg.order_items"),
    ("olist_products_dataset", "SELECT product_id, product_category_name, product_name_lenght, product_description_lenght, product_photos_qty, product_weight_g, product_length_cm, product_height_cm, product_width_cm FROM OlistDW.stg.products"),
    ("olist_sellers_dataset", "SELECT seller_id, seller_zip_code_prefix, seller_city, seller_state FROM OlistDW.stg.sellers"),
    ("olist_order_payments_dataset", "SELECT order_id, payment_sequential, payment_type, payment_installments, payment_value FROM OlistDW.stg.order_payments"),
    ("olist_order_reviews_dataset", "SELECT review_id, order_id, review_score, review_comment_title, review_comment_message, review_creation_date, review_answer_timestamp FROM OlistDW.stg.order_reviews"),
    ("olist_geolocation_dataset", "SELECT geolocation_zip_code_prefix, geolocation_lat, geolocation_lng, geolocation_city, geolocation_state FROM OlistDW.stg.geolocation"),
    ("product_category_name_translation", "SELECT product_category_name, product_category_name_english FROM OlistDW.stg.product_category")
]

print("Converting Olist_OLTP to physical base tables...")
for tbl_name, select_sql in tables:
    # Drop existing view or table
    cur.execute(f"IF OBJECT_ID('dbo.{tbl_name}', 'V') IS NOT NULL DROP VIEW dbo.{tbl_name};")
    cur.execute(f"IF OBJECT_ID('dbo.{tbl_name}', 'U') IS NOT NULL DROP TABLE dbo.{tbl_name};")
    
    # Create physical table
    start_t = time.time()
    cur.execute(f"SELECT * INTO dbo.{tbl_name} FROM ({select_sql}) AS src;")
    cur.execute(f"SELECT COUNT(*) FROM dbo.{tbl_name};")
    cnt = cur.fetchone()[0]
    print(f"  [BASE TABLE] dbo.{tbl_name:35s} : {cnt:>10,} rows ({time.time() - start_t:.2f}s)")

cur.close()
conn_oltp.close()
print("Olist_OLTP physical tables successfully created and populated!")
