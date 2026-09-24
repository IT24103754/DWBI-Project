"""
IT3101 DWBI Project – Olist Brazilian E-Commerce
Script 03: Transform & Load Dimension Tables
  - dim_customer   (from stg.customers)
  - dim_product    (from stg.products + stg.product_category for EN name)
  - dim_seller     (from stg.sellers)
  - dim_geography  (from stg.geolocation - one row per zip prefix)
  - dim_date       (already populated by 02_star_schema.sql)

SCD Type 1: DELETE + full reload (justified: closed 2016-2018 dataset)
Note: Uses DELETE instead of TRUNCATE because fact table FK references dims.
      Run this BEFORE loading the fact table, or fact is cleared first below.
"""

import sys
import time
import pyodbc
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

CONN_STR = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=OlistDW;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

CHUNK_SIZE = 5000


def fetch_df(conn, sql):
    """Execute SQL and return a pandas DataFrame."""
    cursor = conn.cursor()
    cursor.execute(sql)
    cols = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    return pd.DataFrame.from_records(rows, columns=cols)


def log_etl(cursor, conn, pkg, rows, pkg_start, status='SUCCESS', err=None):
    cursor.execute("""
        INSERT INTO dw.etl_run_log
            (package_name, rows_loaded, start_time, end_time, status, error_msg)
        VALUES (?, ?, ?, GETDATE(), ?, ?)
    """, pkg, rows, pkg_start, status, err)
    conn.commit()


def clear_fact_and_dims(conn):
    """Truncate fact first (removes FK dependency), then delete dim rows."""
    cursor = conn.cursor()
    print("  Clearing fact table (for FK-safe dimension reload) ...")
    cursor.execute("TRUNCATE TABLE dw.fact_order_items")
    for tbl in ['dw.dim_customer', 'dw.dim_product', 'dw.dim_seller', 'dw.dim_geography']:
        cursor.execute(f"DELETE FROM {tbl}")
    conn.commit()
    print("  Tables cleared.")


def chunked_insert(cursor, conn, sql, data):
    total = 0
    for i in range(0, len(data), CHUNK_SIZE):
        batch = data[i:i+CHUNK_SIZE]
        cursor.executemany(sql, batch)
        conn.commit()
        total += len(batch)
        print(f"    {total:>7,} / {len(data):,}", end='\r')
    print(f"    {total:,} rows inserted         ")
    return total


def load_dim_customer(conn):
    print("\n  [dim_customer]")
    pkg_start = pd.Timestamp.now()
    cursor = conn.cursor()
    cursor.fast_executemany = True

    df = fetch_df(conn, """
        SELECT DISTINCT
            customer_id,
            customer_city            AS city,
            customer_state           AS state,
            customer_zip_code_prefix AS zip_prefix
        FROM stg.customers
        WHERE customer_id IS NOT NULL
    """)

    df = df.drop_duplicates(subset='customer_id')
    for col in df.select_dtypes('object').columns:
        df[col] = df[col].str.strip().str.title()

    data = [tuple(None if pd.isna(v) else v for v in r)
            for r in df.itertuples(index=False, name=None)]
    sql = """INSERT INTO dw.dim_customer (customer_id, city, state, zip_prefix)
             VALUES (?,?,?,?)"""
    n = chunked_insert(cursor, conn, sql, data)
    log_etl(cursor, conn, '03_dim_customer', n, pkg_start)
    return n


def load_dim_product(conn):
    print("\n  [dim_product]")
    pkg_start = pd.Timestamp.now()
    cursor = conn.cursor()
    cursor.fast_executemany = True

    df = fetch_df(conn, """
        SELECT
            p.product_id,
            p.product_category_name AS category_pt,
            COALESCE(pc.product_category_name_english, p.product_category_name) AS category_en,
            p.product_weight_g      AS weight_g,
            p.product_length_cm     AS length_cm,
            p.product_height_cm     AS height_cm,
            p.product_width_cm      AS width_cm
        FROM stg.products p
        LEFT JOIN stg.product_category pc
               ON p.product_category_name = pc.product_category_name
        WHERE p.product_id IS NOT NULL
    """)

    df = df.drop_duplicates(subset='product_id')
    for col in ['category_pt', 'category_en']:
        df[col] = df[col].str.strip().str.replace('_', ' ', regex=False)
    df['category_en'] = df['category_en'].str.title()

    data = [tuple(None if pd.isna(v) else v for v in r)
            for r in df.itertuples(index=False, name=None)]
    sql = """INSERT INTO dw.dim_product
                (product_id, category_pt, category_en, weight_g, length_cm, height_cm, width_cm)
             VALUES (?,?,?,?,?,?,?)"""
    n = chunked_insert(cursor, conn, sql, data)
    log_etl(cursor, conn, '03_dim_product', n, pkg_start)
    return n


def load_dim_seller(conn):
    print("\n  [dim_seller]")
    pkg_start = pd.Timestamp.now()
    cursor = conn.cursor()
    cursor.fast_executemany = True

    df = fetch_df(conn, """
        SELECT DISTINCT
            seller_id,
            seller_city            AS city,
            seller_state           AS state,
            seller_zip_code_prefix AS zip_prefix
        FROM stg.sellers
        WHERE seller_id IS NOT NULL
    """)

    df = df.drop_duplicates(subset='seller_id')
    for col in df.select_dtypes('object').columns:
        df[col] = df[col].str.strip().str.title()

    data = [tuple(None if pd.isna(v) else v for v in r)
            for r in df.itertuples(index=False, name=None)]
    sql = """INSERT INTO dw.dim_seller (seller_id, city, state, zip_prefix)
             VALUES (?,?,?,?)"""
    n = chunked_insert(cursor, conn, sql, data)
    log_etl(cursor, conn, '03_dim_seller', n, pkg_start)
    return n


def load_dim_geography(conn):
    print("\n  [dim_geography]")
    pkg_start = pd.Timestamp.now()
    cursor = conn.cursor()
    cursor.fast_executemany = True

    df = fetch_df(conn, """
        SELECT
            geolocation_zip_code_prefix AS zip_prefix,
            AVG(geolocation_lat)        AS lat,
            AVG(geolocation_lng)        AS lng,
            MAX(geolocation_city)       AS city,
            MAX(geolocation_state)      AS state
        FROM stg.geolocation
        WHERE geolocation_zip_code_prefix IS NOT NULL
        GROUP BY geolocation_zip_code_prefix
    """)

    df = df.drop_duplicates(subset='zip_prefix')
    # Cast numeric columns explicitly (pyodbc may return Decimal as object)
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lng'] = pd.to_numeric(df['lng'], errors='coerce')
    for col in ['city', 'state', 'zip_prefix']:
        if col in df.columns and df[col].dtype == object:
            df[col] = df[col].str.strip().str.title()

    data = [tuple(None if pd.isna(v) else v for v in r)
            for r in df.itertuples(index=False, name=None)]
    sql = """INSERT INTO dw.dim_geography (zip_prefix, lat, lng, city, state)
             VALUES (?,?,?,?,?)"""
    n = chunked_insert(cursor, conn, sql, data)
    log_etl(cursor, conn, '03_dim_geography', n, pkg_start)
    return n


def main():
    print("="*60)
    print("  PKG_03 - Transform & Load Dimension Tables")
    print("="*60)

    t0 = time.time()
    conn = pyodbc.connect(CONN_STR, autocommit=False)

    # Truncate fact first so FK constraints don't block dim DELETE
    clear_fact_and_dims(conn)

    load_dim_customer(conn)
    load_dim_product(conn)
    load_dim_seller(conn)
    load_dim_geography(conn)

    conn.close()
    print(f"\n  PKG_03 COMPLETE in {time.time()-t0:.1f}s")


if __name__ == '__main__':
    main()
