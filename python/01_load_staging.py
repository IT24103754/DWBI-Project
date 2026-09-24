"""
IT3101 DWBI Project – Olist Brazilian E-Commerce
Script 01: Load all 9 CSVs into stg.* staging tables
Uses pandas + pyodbc for fast chunked loading
"""

import os
import sys
import time
import pyodbc
import pandas as pd

# Force UTF-8 output on Windows console
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── Connection ─────────────────────────────────────────────────
SERVER   = 'localhost'
DATABASE = 'OlistDW'
CONN_STR = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'Dataset')

# ── CSV → staging table mapping ─────────────────────────────────
CSV_MAP = {
    'olist_customers_dataset.csv':          'stg.customers',
    'olist_orders_dataset.csv':             'stg.orders',
    'olist_order_items_dataset.csv':        'stg.order_items',
    'olist_order_payments_dataset.csv':     'stg.order_payments',
    'olist_order_reviews_dataset.csv':      'stg.order_reviews',
    'olist_products_dataset.csv':           'stg.products',
    'olist_sellers_dataset.csv':            'stg.sellers',
    'olist_geolocation_dataset.csv':        'stg.geolocation',
    'product_category_name_translation.csv':'stg.product_category',
}

# Column dtypes to avoid SSIS-style float inference on ID columns
DTYPE_OVERRIDES = {
    'customer_id':              str,
    'customer_unique_id':       str,
    'customer_zip_code_prefix': str,
    'order_id':                 str,
    'product_id':               str,
    'seller_id':                str,
    'review_id':                str,
    'geolocation_zip_code_prefix': str,
    'seller_zip_code_prefix':   str,
}

DATETIME_COLS = {
    'stg.orders': [
        'order_purchase_timestamp', 'order_approved_at',
        'order_delivered_carrier_date', 'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ],
    'stg.order_items':    ['shipping_limit_date'],
    'stg.order_reviews':  ['review_creation_date', 'review_answer_timestamp'],
}

CHUNK_SIZE = 5000


def log_etl(conn, package_name, rows_loaded, start_time, status='SUCCESS', error_msg=None):
    """Write to dw.etl_run_log."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO dw.etl_run_log
            (package_name, rows_loaded, start_time, end_time, status, error_msg)
        VALUES (?, ?, ?, GETDATE(), ?, ?)
    """, package_name, rows_loaded, start_time, status, error_msg)
    conn.commit()


def load_csv(conn, csv_file, table):
    """Load a CSV file into a staging table using fast_executemany."""
    csv_path = os.path.join(DATA_DIR, csv_file)
    print(f"  Loading {csv_file} -> {table} ...")
    start = time.time()
    pkg_start = pd.Timestamp.now()

    # Read CSV
    df = pd.read_csv(
        csv_path,
        dtype=DTYPE_OVERRIDES,
        low_memory=False,
        encoding='utf-8'
    )

    # Parse datetime columns
    for col in DATETIME_COLS.get(table, []):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Strip whitespace from string columns
    str_cols = df.select_dtypes(include='object').columns
    df[str_cols] = df[str_cols].apply(lambda c: c.str.strip())

    # Drop stg_load_dt if present (SQL has DEFAULT)
    if 'stg_load_dt' in df.columns:
        df.drop(columns=['stg_load_dt'], inplace=True)

    total_rows = len(df)

    # Truncate target table before load
    cursor = conn.cursor()
    cursor.execute(f"TRUNCATE TABLE {table}")
    conn.commit()

    # Build parameterised INSERT
    cols    = ', '.join(df.columns)
    params  = ', '.join(['?'] * len(df.columns))
    sql     = f"INSERT INTO {table} ({cols}) VALUES ({params})"

    # Fast chunked insert
    cursor.fast_executemany = True
    inserted = 0
    for i in range(0, total_rows, CHUNK_SIZE):
        chunk = df.iloc[i:i+CHUNK_SIZE]
        # Replace NaN with None so pyodbc sends NULL
        data = [
            tuple(None if pd.isna(v) else v for v in row)
            for row in chunk.itertuples(index=False, name=None)
        ]
        cursor.executemany(sql, data)
        conn.commit()
        inserted += len(data)
        print(f"    {inserted:>7,} / {total_rows:,} rows", end='\r')

    elapsed = time.time() - start
    print(f"    {total_rows:,} rows loaded in {elapsed:.1f}s          ")
    log_etl(conn, f'01_load_staging:{table}', total_rows, pkg_start)
    return total_rows


def main():
    print("="*60)
    print("  PKG_01 – Extract & Load Staging")
    print("="*60)

    conn = pyodbc.connect(CONN_STR, autocommit=False)
    total = 0

    for csv_file, table in CSV_MAP.items():
        try:
            rows = load_csv(conn, csv_file, table)
            total += rows
        except Exception as e:
            print(f"  [ERROR] {csv_file}: {e}")
            log_etl(conn, f'01_load_staging:{table}', 0,
                    pd.Timestamp.now(), 'ERROR', str(e))

    conn.close()
    print(f"\n  TOTAL rows loaded into staging: {total:,}")
    print("  PKG_01 COMPLETE")


if __name__ == '__main__':
    main()
