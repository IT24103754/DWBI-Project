"""
IT3101 DWBI Project – Olist Brazilian E-Commerce
Script 05: Analytical queries (insight validation)
Run AFTER full ETL to validate the 5 business hypotheses
Outputs results to console and saves CSV summaries to docs/
"""

import os
import sys
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

DOCS_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')
os.makedirs(DOCS_DIR, exist_ok=True)


def run_query(conn, title, sql, out_file=None):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)
    df = pd.read_sql(sql, conn)
    print(df.to_string(index=False))
    if out_file:
        path = os.path.join(DOCS_DIR, out_file)
        df.to_csv(path, index=False)
        print(f"  → Saved: {out_file}")
    return df


def main():
    conn = pyodbc.connect(CONN_STR, autocommit=True)

    # ── Hypothesis 1 ──────────────────────────────────────────
    # Delivery delay correlates with lower review scores
    run_query(conn,
        "H1: Delivery Delay vs Review Score",
        """
        SELECT
            CASE
                WHEN delivery_delay_days < -7 THEN 'Very Early (>7 days)'
                WHEN delivery_delay_days < 0  THEN 'Early (1-7 days)'
                WHEN delivery_delay_days = 0  THEN 'On Time'
                WHEN delivery_delay_days <= 7 THEN 'Late (1-7 days)'
                ELSE 'Very Late (>7 days)'
            END AS delay_bucket,
            COUNT(*)                               AS orders,
            AVG(CAST(review_score AS FLOAT))       AS avg_review_score,
            AVG(CAST(delivery_delay_days AS FLOAT)) AS avg_delay
        FROM dw.fact_order_items
        WHERE delivery_delay_days IS NOT NULL AND review_score IS NOT NULL
        GROUP BY
            CASE
                WHEN delivery_delay_days < -7 THEN 'Very Early (>7 days)'
                WHEN delivery_delay_days < 0  THEN 'Early (1-7 days)'
                WHEN delivery_delay_days = 0  THEN 'On Time'
                WHEN delivery_delay_days <= 7 THEN 'Late (1-7 days)'
                ELSE 'Very Late (>7 days)'
            END
        ORDER BY avg_delay
        """,
        'h1_delay_vs_review.csv'
    )

    # ── Hypothesis 2 ──────────────────────────────────────────
    # States with high freight relative to order value
    run_query(conn,
        "H2: Freight Cost Relative to Order Value by State",
        """
        SELECT TOP 15
            c.state,
            COUNT(*)                                  AS orders,
            AVG(f.price_brl)                          AS avg_price_brl,
            AVG(f.freight_value)                      AS avg_freight_brl,
            AVG(f.freight_value / NULLIF(f.price_brl,0)) * 100 AS freight_pct_of_price
        FROM dw.fact_order_items f
        JOIN dw.dim_customer c ON f.customer_key = c.customer_key
        WHERE f.price_brl > 0
        GROUP BY c.state
        HAVING COUNT(*) > 100
        ORDER BY freight_pct_of_price DESC
        """,
        'h2_freight_by_state.csv'
    )

    # ── Hypothesis 3 ──────────────────────────────────────────
    # Seasonal revenue – November Black Friday spike
    run_query(conn,
        "H3: Monthly Revenue – Black Friday Seasonality",
        """
        SELECT
            d.year,
            d.month,
            d.month_name,
            COUNT(DISTINCT f.order_id)   AS distinct_orders,
            SUM(f.price_brl)             AS revenue_brl,
            SUM(f.price_usd)             AS revenue_usd
        FROM dw.fact_order_items f
        JOIN dw.dim_date d ON f.date_key = d.date_key
        GROUP BY d.year, d.month, d.month_name
        ORDER BY d.year, d.month
        """,
        'h3_monthly_revenue.csv'
    )

    # ── Hypothesis 4 ──────────────────────────────────────────
    # Small number of sellers cause most late deliveries
    run_query(conn,
        "H4: Top 20 Sellers Responsible for Late Deliveries",
        """
        SELECT TOP 20
            s.seller_id,
            s.state                                        AS seller_state,
            COUNT(*)                                       AS total_orders,
            SUM(CASE WHEN f.delivery_delay_days > 0 THEN 1 ELSE 0 END) AS late_orders,
            CAST(SUM(CASE WHEN f.delivery_delay_days > 0 THEN 1 ELSE 0 END) AS FLOAT)
                / COUNT(*) * 100                           AS pct_late,
            AVG(CAST(f.delivery_delay_days AS FLOAT))      AS avg_delay
        FROM dw.fact_order_items f
        JOIN dw.dim_seller s ON f.seller_key = s.seller_key
        WHERE f.delivery_delay_days IS NOT NULL
        GROUP BY s.seller_id, s.state
        HAVING COUNT(*) >= 20
        ORDER BY late_orders DESC
        """,
        'h4_late_sellers.csv'
    )

    # ── Hypothesis 5 ──────────────────────────────────────────
    # Categories with low review scores regardless of delivery time
    run_query(conn,
        "H5: Product Categories with Low Reviews (delivery-adjusted)",
        """
        SELECT
            p.category_en,
            COUNT(*)                                       AS order_items,
            AVG(CAST(f.review_score AS FLOAT))             AS avg_review_score,
            AVG(CAST(f.delivery_delay_days AS FLOAT))      AS avg_delay_days,
            AVG(f.price_brl)                               AS avg_price_brl
        FROM dw.fact_order_items f
        JOIN dw.dim_product p ON f.product_key = p.product_key
        WHERE f.review_score IS NOT NULL
        GROUP BY p.category_en
        HAVING COUNT(*) > 50
        ORDER BY avg_review_score ASC
        """,
        'h5_category_reviews.csv'
    )

    conn.close()
    print("\n  All hypothesis queries complete. CSVs saved to docs/")


if __name__ == '__main__':
    main()
