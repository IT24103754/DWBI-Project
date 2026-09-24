"""
IT3101 DWBI Project - Olist Brazilian E-Commerce
Script 04: Transform & Load Fact Table (SQL-based key resolution)
  - Builds a staging view joining all source tables
  - Resolves all surrogate keys directly in SQL (avoids Python map() trim issues)
  - Inserts into dw.fact_order_items in chunks
"""

import sys
import time
import pyodbc
import pandas as pd
from decimal import Decimal

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

CONN_STR = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=OlistDW;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

CHUNK_SIZE = 5000

# -----------------------------------------------------------------------
# Full SQL to resolve all keys and compute derived columns in one query
# -----------------------------------------------------------------------
FACT_SQL = """
SELECT
    oi.order_id,
    oi.order_item_id,
    dc.customer_key,
    dp.product_key,
    ds.seller_key,
    CONVERT(INT, FORMAT(CONVERT(DATE, o.order_purchase_timestamp), 'yyyyMMdd')) AS date_key,
    dg.geo_key,                        -- nullable: LEFT JOIN
    oi.price                           AS price_brl,
    ROUND(oi.price * er.usd_per_brl, 2) AS price_usd,
    oi.freight_value,
    rv.review_score,
    DATEDIFF(day,
        o.order_estimated_delivery_date,
        o.order_delivered_customer_date)  AS delivery_delay_days,
    o.order_status,
    py.payment_type,
    py.payment_value
FROM stg.order_items oi
-- Orders (for customer_id + dates + status)
JOIN stg.orders o
    ON oi.order_id = o.order_id
-- Dimension lookups (INNER = must match)
JOIN dw.dim_customer dc
    ON LTRIM(RTRIM(o.customer_id)) = LTRIM(RTRIM(dc.customer_id))
JOIN dw.dim_product dp
    ON LTRIM(RTRIM(oi.product_id)) = LTRIM(RTRIM(dp.product_id))
JOIN dw.dim_seller ds
    ON LTRIM(RTRIM(oi.seller_id)) = LTRIM(RTRIM(ds.seller_id))
JOIN dw.dim_date dd
    ON CONVERT(INT, FORMAT(CONVERT(DATE, o.order_purchase_timestamp), 'yyyyMMdd'))
       = dd.date_key
-- Exchange rates
LEFT JOIN stg.exchange_rates er
    ON CONVERT(DATE, o.order_purchase_timestamp) = er.rate_date
-- Geography (nullable)
LEFT JOIN stg.customers cust
    ON LTRIM(RTRIM(o.customer_id)) = LTRIM(RTRIM(cust.customer_id))
LEFT JOIN dw.dim_geography dg
    ON LTRIM(RTRIM(cust.customer_zip_code_prefix)) = LTRIM(RTRIM(dg.zip_prefix))
-- Reviews (one per order, first only)
LEFT JOIN (
    SELECT order_id, review_score
    FROM (
        SELECT order_id, review_score,
               ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_id) AS rn
        FROM stg.order_reviews
        WHERE review_score IS NOT NULL
    ) r WHERE rn = 1
) rv ON oi.order_id = rv.order_id
-- Payments (sum per order)
LEFT JOIN (
    SELECT order_id,
           MAX(payment_type)  AS payment_type,
           SUM(payment_value) AS payment_value
    FROM stg.order_payments
    GROUP BY order_id
) py ON oi.order_id = py.order_id
"""


def fetch_df(conn, sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    cols = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    converted = []
    for row in rows:
        converted.append(tuple(
            float(v) if isinstance(v, Decimal) else v for v in row
        ))
    return pd.DataFrame.from_records(converted, columns=cols)


def log_etl(cursor, conn, pkg, rows, pkg_start, status='SUCCESS', err=None):
    cursor.execute("""
        INSERT INTO dw.etl_run_log
            (package_name, rows_loaded, start_time, end_time, status, error_msg)
        VALUES (?, ?, ?, GETDATE(), ?, ?)
    """, pkg, rows, pkg_start, status, err)
    conn.commit()


def main():
    print("="*60)
    print("  PKG_04 - Transform & Load Fact Table (SQL key resolution)")
    print("="*60)

    t0 = time.time()
    conn = pyodbc.connect(CONN_STR, autocommit=False)
    cursor = conn.cursor()
    cursor.fast_executemany = True
    pkg_start = pd.Timestamp.now()

    # Step 1: Clear fact table
    print("  Truncating dw.fact_order_items ...")
    cursor.execute("TRUNCATE TABLE dw.fact_order_items")
    conn.commit()

    # Step 2: Build fact data via SQL
    print("  Executing SQL join (all key resolution in SQL) ...")
    df = fetch_df(conn, FACT_SQL)
    print(f"  SQL returned {len(df):,} rows")

    if len(df) == 0:
        print("  [ERROR] No rows returned - check staging tables are populated")
        conn.close()
        return

    # Step 3: Drop duplicates on (order_id, order_item_id)
    df = df.drop_duplicates(subset=['order_id', 'order_item_id'])
    print(f"  After dedup: {len(df):,} rows")

    # Step 4: Convert int columns
    for col in ['customer_key', 'product_key', 'seller_key', 'date_key']:
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
    df['geo_key'] = pd.to_numeric(df['geo_key'], errors='coerce')  # nullable

    # Step 5: Insert in chunks
    sql = """
        INSERT INTO dw.fact_order_items
            (order_id, order_item_id,
             customer_key, product_key, seller_key, date_key, geo_key,
             price_brl, price_usd, freight_value,
             review_score, delivery_delay_days,
             order_status, payment_type, payment_value)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """

    fact_cols = [
        'order_id', 'order_item_id',
        'customer_key', 'product_key', 'seller_key', 'date_key', 'geo_key',
        'price_brl', 'price_usd', 'freight_value',
        'review_score', 'delivery_delay_days',
        'order_status', 'payment_type', 'payment_value'
    ]
    df_fact = df[fact_cols]

    import numpy as np

    data = []
    for row in df_fact.itertuples(index=False, name=None):
        clean = []
        for v in row:
            if v is None or (isinstance(v, float) and pd.isna(v)):
                clean.append(None)
            elif isinstance(v, (np.integer,)):
                clean.append(int(v))
            elif isinstance(v, (np.floating,)):
                clean.append(None if np.isnan(v) else float(v))
            elif hasattr(v, '_value') and v is pd.NA:  # pandas NA
                clean.append(None)
            else:
                clean.append(v)
        data.append(tuple(clean))

    total = 0
    for i in range(0, len(data), CHUNK_SIZE):
        batch = data[i:i+CHUNK_SIZE]
        cursor.executemany(sql, batch)
        conn.commit()
        total += len(batch)
        print(f"    {total:>7,} / {len(data):,} rows", end='\r')

    print(f"    {total:,} rows inserted into dw.fact_order_items         ")
    log_etl(cursor, conn, '04_fact_order_items', total, pkg_start)

    conn.close()
    print(f"\n  {total:,} fact rows loaded in {time.time()-t0:.1f}s")
    print("  PKG_04 COMPLETE")


if __name__ == '__main__':
    main()
