"""
IT3101 DWBI Project - Olist Brazilian E-Commerce
Script 02b: Seed exchange rates using a fixed BRL/USD rate table.
Used as fallback when Frankfurter API is slow/unavailable.

Historical BRL->USD approximate monthly averages 2016-2018:
  2016: ~0.285  2017: ~0.314  2018: ~0.268
We interpolate a rate per year-quarter for accuracy.
"""

import sys
import pyodbc
import pandas as pd
from datetime import date, timedelta

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

CONN_STR = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=OlistDW;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

# Approximate quarterly USD per 1 BRL (historical averages)
QUARTERLY_RATES = {
    (2015, 1): 0.3175, (2015, 2): 0.3143, (2015, 3): 0.2857, (2015, 4): 0.2632,
    (2016, 1): 0.2710, (2016, 2): 0.2830, (2016, 3): 0.3020, (2016, 4): 0.2950,
    (2017, 1): 0.3195, (2017, 2): 0.3106, (2017, 3): 0.3185, (2017, 4): 0.3040,
    (2018, 1): 0.3095, (2018, 2): 0.2770, (2018, 3): 0.2565, (2018, 4): 0.2660,
    (2019, 1): 0.2625, (2019, 2): 0.2580, (2019, 3): 0.2530, (2019, 4): 0.2495,
}

def get_rate(d: date) -> float:
    q = (d.month - 1) // 3 + 1
    return QUARTERLY_RATES.get((d.year, q), 0.28)   # default fallback

def main():
    print("="*60)
    print("  PKG_02b - Seed Exchange Rates (Historical Averages)")
    print("="*60)

    conn = pyodbc.connect(CONN_STR, autocommit=False)
    cursor = conn.cursor()
    pkg_start = pd.Timestamp.now()

    # Get all unique order dates from staging
    cursor.execute("""
        SELECT DISTINCT CONVERT(DATE, order_purchase_timestamp) AS order_date
        FROM stg.orders
        WHERE order_purchase_timestamp IS NOT NULL
        ORDER BY order_date
    """)
    dates = [row[0] for row in cursor.fetchall()]
    print(f"  Unique order dates: {len(dates)}")
    print(f"  Date range: {dates[0]} -> {dates[-1]}")

    rows = []
    for d in dates:
        usd_per_brl = get_rate(d)
        brl_per_usd = round(1 / usd_per_brl, 6)
        rows.append((d, round(brl_per_usd, 6), round(usd_per_brl, 6)))

    cursor.execute("TRUNCATE TABLE stg.exchange_rates")
    cursor.fast_executemany = True
    cursor.executemany(
        "INSERT INTO stg.exchange_rates (rate_date, brl_per_usd, usd_per_brl) VALUES (?,?,?)",
        rows
    )
    conn.commit()

    cursor.execute("""
        INSERT INTO dw.etl_run_log
            (package_name, rows_loaded, start_time, end_time, status)
        VALUES (?, ?, ?, GETDATE(), ?)
    """, '02b_exchange_rates_seed', len(rows), pkg_start, 'SUCCESS')
    conn.commit()
    conn.close()

    print(f"  Loaded {len(rows)} exchange rate rows into stg.exchange_rates")
    print("  PKG_02b COMPLETE")

if __name__ == '__main__':
    main()
