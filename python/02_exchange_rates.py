"""
IT3101 DWBI Project – Olist Brazilian E-Commerce
Script 02: Fetch BRL→USD exchange rates from Frankfurter API
Loads into stg.exchange_rates for every unique order date in stg.orders

API: https://api.frankfurter.app/{date}?from=BRL&to=USD
Free, no key required.
"""

import sys
import time
import requests
import pyodbc
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── Connection ─────────────────────────────────────────────────
CONN_STR = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=OlistDW;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

API_BASE    = "https://api.frankfurter.app"
BATCH_PAUSE = 0.25   # seconds between API calls (be polite)


def fetch_rate(date_str: str) -> float | None:
    """Fetch BRL→USD rate for a given date (YYYY-MM-DD). Returns USD per 1 BRL."""
    try:
        resp = requests.get(
            f"{API_BASE}/{date_str}",
            params={"from": "BRL", "to": "USD"},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            return data['rates']['USD']
        elif resp.status_code == 404:
            # Weekend / holiday – try to find closest business day
            return None
        else:
            print(f"    [WARN] API {resp.status_code} for {date_str}")
            return None
    except Exception as e:
        print(f"    [ERROR] {date_str}: {e}")
        return None


def get_unique_order_dates(conn) -> list[str]:
    """Return all unique purchase dates from stg.orders."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT CONVERT(DATE, order_purchase_timestamp) AS order_date
        FROM stg.orders
        WHERE order_purchase_timestamp IS NOT NULL
        ORDER BY order_date
    """)
    return [str(row[0]) for row in cursor.fetchall()]


def fill_weekend_rates(rates: dict) -> dict:
    """
    For dates with no rate (weekend/holiday), fill forward from
    the nearest prior business day.
    """
    dates = sorted(rates.keys())
    last_valid = None
    for d in dates:
        if rates[d] is not None:
            last_valid = rates[d]
        elif last_valid is not None:
            rates[d] = last_valid
    return rates


def main():
    print("="*60)
    print("  PKG_02 – Exchange Rate API Fetch (Frankfurter)")
    print("="*60)

    conn = pyodbc.connect(CONN_STR, autocommit=False)
    pkg_start = pd.Timestamp.now()

    dates = get_unique_order_dates(conn)
    print(f"  Unique order dates: {len(dates)}")
    print(f"  Date range: {dates[0]} -> {dates[-1]}")

    # Fetch rates
    rates = {}
    for i, d in enumerate(dates):
        rate = fetch_rate(d)
        rates[d] = rate
        if (i + 1) % 50 == 0:
            print(f"    Fetched {i+1}/{len(dates)} dates ...")
        time.sleep(BATCH_PAUSE)

    # Fill weekends/holidays
    rates = fill_weekend_rates(rates)

    # Insert into stg.exchange_rates (MERGE to avoid duplicates)
    cursor = conn.cursor()
    cursor.fast_executemany = True

    rows = []
    for d, usd_per_brl in rates.items():
        if usd_per_brl is None:
            continue
        brl_per_usd = round(1 / usd_per_brl, 6) if usd_per_brl else None
        rows.append((d, brl_per_usd, usd_per_brl))

    # Truncate and reload
    cursor.execute("TRUNCATE TABLE stg.exchange_rates")
    cursor.executemany(
        "INSERT INTO stg.exchange_rates (rate_date, brl_per_usd, usd_per_brl) VALUES (?,?,?)",
        rows
    )
    conn.commit()

    # Log ETL
    cursor.execute("""
        INSERT INTO dw.etl_run_log
            (package_name, rows_loaded, start_time, end_time, status)
        VALUES (?, ?, ?, GETDATE(), ?)
    """, '02_exchange_rates', len(rows), pkg_start, 'SUCCESS')
    conn.commit()
    conn.close()

    print(f"  Loaded {len(rows)} exchange rate rows into stg.exchange_rates")
    print("  PKG_02 COMPLETE")


if __name__ == '__main__':
    main()
