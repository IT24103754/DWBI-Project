# IT3101 – Data Warehouse & BI Project Design
## Olist Brazilian E-Commerce — SQL Server / SSMS / SSIS / SSAS Build Spec (for Antigravity)

---

## 0. Project Summary

**Business scenario:** Olist, a Brazilian marketplace connecting small sellers to major e-commerce channels, needs an analytical platform to monitor sales performance, delivery/logistics efficiency, and customer satisfaction across 2016–2018.

**Why this dataset fits the brief:** Real, anonymized OLTP-style transactional data (not synthetic), ~100K orders / 112K order items, 9 naturally related entities, genuine data quality issues worth cleaning, and clear business questions to answer.

**Sources (3 types, to satisfy Task 2's "multiple source types"):**
1. **CSV files** — the 9 Olist Kaggle CSVs (primary source)
2. **Relational database** — loaded via SSIS/BULK INSERT into a SQL Server "OLTP simulation" schema with proper PK/FK constraints — this is your operational source system
3. **API** — pull historical BRL→USD exchange rates from a free API (e.g. Frankfurter API) via a script/SSIS Script Task, enrich the fact table with `price_usd`

---

## 1. Software Stack (all Windows — Power BI needs Windows anyway)

| Tool | Role |
|---|---|
| **SQL Server Developer Edition** (free) | Your database engine — staging, star schema, all T-SQL |
| **SSMS** (SQL Server Management Studio) | Write/run T-SQL, manage tables, inspect data |
| **SSDT** (SQL Server Data Tools, Visual Studio workload) | Where you build SSIS packages and SSAS projects |
| **SSIS** (SQL Server Integration Services) | Visual ETL: CSV → Staging → Star Schema |
| **SSAS** (SQL Server Analysis Services, Tabular mode) | Builds the OLAP cube/semantic model on top of the star schema |
| **Power BI Desktop** | Connects live to the SSAS model for dashboards |
| **draw.io / diagrams.net** | Architecture + star schema diagrams |
| **Python** (optional) | Only if you prefer scripting the exchange-rate API pull outside SSIS |
| **Google Antigravity** | Agentic IDE to generate T-SQL scripts, SSIS package XML/BIML, and validation tests |
| **Git** | Version control / submission |

> Use **SSAS Tabular**, not Multidimensional — Tabular is simpler to build in SSDT, performs well at this data volume, and Power BI connects to it natively via DAX (Multidimensional needs MDX and is heavier to set up for a coursework timeline).

---

## 2. Task 1 — Dataset Overview

| Field | Value |
|---|---|
| Business domain | Retail / E-commerce |
| Purpose | Multi-seller marketplace order fulfillment platform |
| Business problem | Olist needs visibility into sales trends, delivery performance, and customer satisfaction across sellers and regions |
| Dataset source | Kaggle — `olistbr/brazilian-ecommerce` |
| Format | 9 CSV files (+ SQL Server relational copy + 1 API feed) |
| Records | 99,441 orders / 112,650 order items / 99,441 customers / 32,951 products / 3,095 sellers / 1,000,163 geolocation rows |
| Time span | 2016–2018 |

Source tables: `olist_orders`, `olist_order_items`, `olist_customers`, `olist_products`, `olist_sellers`, `olist_order_payments`, `olist_order_reviews`, `olist_geolocation`, `product_category_name_translation`

---

## 3. Task 2 — Source Preparation Plan

| Source | Type | How it's used |
|---|---|---|
| 9 Olist CSVs | File | Loaded via SSIS Flat File Source / `BULK INSERT` into staging |
| SQL Server staging DB | Relational DB | Normalized tables with FKs — your "operational system" |
| Exchange rate API | REST API | Pulled per unique order date (Script Task in SSIS, or a small Python/PowerShell step), joined onto the fact load |

---

## 4. Task 3 — Architecture

```
┌─────────────────────┐
│   SOURCE LAYER        │  CSV files | SQL Server OLTP copy | Exchange Rate API
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ DATA INTEGRATION LAYER│  SSIS packages — Extract → Transform → Load
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│   STORAGE LAYER        │
│  ├─ Staging schema     │  raw, untransformed loads (SQL Server)
│  ├─ EDW (star schema)  │  fact_order_items + 5 dimensions
│  └─ Data Mart          │  logistics_performance_mart (view/table)
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│   SEMANTIC/OLAP LAYER  │  SSAS Tabular model (measures, hierarchies, KPIs)
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│  PRESENTATION LAYER    │  Power BI Desktop — 3 report pages, live connection to SSAS
└───────────────────────┘
```

---

## 5. Task 4 — Dimensional Model (Star Schema)

**Grain:** one row per order item.

### Fact table: `fact_order_items`
```sql
CREATE TABLE dw.fact_order_items (
    order_item_key   INT IDENTITY PRIMARY KEY,
    order_id         VARCHAR(50) NOT NULL,
    order_item_id    INT NOT NULL,
    customer_key     INT FOREIGN KEY REFERENCES dw.dim_customer(customer_key),
    product_key      INT FOREIGN KEY REFERENCES dw.dim_product(product_key),
    seller_key       INT FOREIGN KEY REFERENCES dw.dim_seller(seller_key),
    date_key         INT FOREIGN KEY REFERENCES dw.dim_date(date_key),
    geo_key          INT FOREIGN KEY REFERENCES dw.dim_geography(geo_key),
    price_brl        DECIMAL(10,2),
    price_usd        DECIMAL(10,2),
    freight_value    DECIMAL(10,2),
    review_score     TINYINT,
    delivery_delay_days INT
);
```

### Dimension tables
```sql
CREATE TABLE dw.dim_customer (
    customer_key INT IDENTITY PRIMARY KEY,
    customer_id  VARCHAR(50),
    city         VARCHAR(100),
    state        VARCHAR(5),
    zip_prefix   VARCHAR(10)
);

CREATE TABLE dw.dim_product (
    product_key  INT IDENTITY PRIMARY KEY,
    product_id   VARCHAR(50),
    category_en  VARCHAR(100),
    weight_g     INT,
    length_cm    INT,
    height_cm    INT,
    width_cm     INT
);

CREATE TABLE dw.dim_seller (
    seller_key   INT IDENTITY PRIMARY KEY,
    seller_id    VARCHAR(50),
    city         VARCHAR(100),
    state        VARCHAR(5)
);

CREATE TABLE dw.dim_date (
    date_key     INT PRIMARY KEY,      -- yyyymmdd
    full_date    DATE,
    day          TINYINT,
    month        TINYINT,
    quarter      TINYINT,
    year         SMALLINT,
    weekday_name VARCHAR(10)
);

CREATE TABLE dw.dim_geography (
    geo_key     INT IDENTITY PRIMARY KEY,
    zip_prefix  VARCHAR(10),
    lat         DECIMAL(9,6),
    lng         DECIMAL(9,6),
    city        VARCHAR(100),
    state       VARCHAR(5)
);
```

**Design assumption:** SCD Type 1 across all dimensions — this is closed historical data (2016–2018), not a live-changing source, so overwrite-on-update is justified and should be stated explicitly in your report.

---

## 6. Task 5 — ETL Pipeline (SSIS)

Build as **3 separate SSIS packages** (cleaner to demo + debug in Antigravity than one monolith):

1. **`PKG_01_Extract_Load_Staging.dtsx`**
   - Flat File Sources for all 9 CSVs → OLE DB Destinations into `stg.*` tables
   - Script Task calls the exchange-rate API once per unique order date, writes to `stg.exchange_rates`

2. **`PKG_02_Transform_Load_DimTables.dtsx`**
   - Data Conversion / Derived Column transforms: category name translation join, null handling on `review_comment_message`, type fixes on ID columns (keep as string, don't let SSIS infer float)
   - Lookup transforms to dedupe and generate surrogate keys
   - Loads `dw.dim_customer`, `dw.dim_product`, `dw.dim_seller`, `dw.dim_date`, `dw.dim_geography`

3. **`PKG_03_Transform_Load_FactTable.dtsx`**
   - Deduplicate `stg.order_items` on (order_id, order_item_id)
   - Derived Column: `delivery_delay_days = DATEDIFF("dd", estimated_date, delivered_date)`
   - Lookup transforms against each dim table to resolve surrogate keys
   - Merge Join against `stg.exchange_rates` for `price_usd`
   - Load into `dw.fact_order_items`

Add an `etl_run_log` table (run_id, package_name, rows_loaded, start_time, end_time) written to via an Execute SQL Task at the end of each package — this is your validation evidence for Task 5's documentation requirement.

```sql
CREATE TABLE dw.etl_run_log (
    run_id INT IDENTITY PRIMARY KEY,
    package_name VARCHAR(100),
    rows_loaded INT,
    start_time DATETIME,
    end_time DATETIME
);
```

---

## 7. Task 6 — Data Mart

**`dw.logistics_performance_mart`** (built as an indexed view or materialized table on top of the EDW)
```sql
CREATE VIEW dw.logistics_performance_mart AS
SELECT
    s.state AS seller_state,
    c.state AS customer_state,
    d.year, d.month,
    AVG(f.delivery_delay_days) AS avg_delay,
    AVG(f.freight_value) AS avg_freight,
    AVG(CAST(f.review_score AS FLOAT)) AS avg_review_score,
    COUNT(*) AS order_item_count
FROM dw.fact_order_items f
JOIN dw.dim_seller s ON f.seller_key = s.seller_key
JOIN dw.dim_customer c ON f.customer_key = c.customer_key
JOIN dw.dim_date d ON f.date_key = d.date_key
GROUP BY s.state, c.state, d.year, d.month;
```
- Purpose: focused view for Operations/Logistics managers on delivery and freight performance without querying the full fact table
- Target users: Operations team
- Analytical benefit: pre-aggregated, isolates delivery-related measures from the noisier full grain

---

## 8. Task 7 — SSAS Tabular Model + Power BI Dashboard

**SSAS Tabular model (built in SSDT):**
- Import `dw.fact_order_items` + all 5 dimensions
- Relationships: fact → each dim on surrogate keys (many-to-one)
- **Measures (DAX):**
  - `Total Revenue = SUM(fact_order_items[price_brl])`
  - `Total Revenue USD = SUM(fact_order_items[price_usd])`
  - `Avg Delivery Delay = AVERAGE(fact_order_items[delivery_delay_days])`
  - `Avg Review Score = AVERAGE(fact_order_items[review_score])`
  - `Order Count = DISTINCTCOUNT(fact_order_items[order_id])`
- **Hierarchies:** `dim_date`: Year → Quarter → Month → Day; `dim_geography`: State → City
- Deploy the model to your local SSAS instance

**Power BI Desktop** connects **live** to the SSAS model (Connect Live, not Import) so it behaves as a true OLAP front-end:

- **Page 1 – Executive Summary:** KPI cards (Total Revenue, Order Count, Avg Review Score, Avg Delivery Delay), trend sparkline
- **Page 2 – Trend Analysis:** monthly revenue line chart, avg delivery delay over time, top-10 category bar chart
- **Page 3 – Interactive Analysis:** map (dim_geography lat/lng), slicers (state, category, year), drill-down on the date hierarchy, roll-up on geography hierarchy

---

## 9. Task 8 — Insight Hypotheses to Validate (need ≥5, with evidence)

1. Orders with longer delivery delays correlate with lower review scores.
2. Certain states have disproportionately higher freight cost relative to order value.
3. Revenue is seasonal — spikes around November (Black Friday equivalent).
4. A small number of sellers account for a disproportionate share of late deliveries.
5. Some product categories have consistently lower review scores independent of delivery time (product-quality issue, not logistics).

Each becomes: chart → statement → recommendation.

---

## 10. Repo / Project Structure

```
olist-dwbi-project/
├── data/raw/                          # original CSVs
├── sql/
│   ├── 01_staging_schema.sql
│   ├── 02_star_schema.sql
│   ├── 03_data_mart.sql
│   └── 04_etl_run_log.sql
├── ssis/
│   ├── PKG_01_Extract_Load_Staging.dtsx
│   ├── PKG_02_Transform_Load_DimTables.dtsx
│   └── PKG_03_Transform_Load_FactTable.dtsx
├── ssas/
│   └── OlistTabularModel/             # SSDT SSAS project
├── docs/
│   ├── architecture_diagram.png
│   ├── star_schema_diagram.png
│   └── data_catalog.md
├── powerbi/
│   └── olist_dashboard.pbix
└── README.md
```

---

## 11. Suggested Antigravity build prompts (run in stages)

**Stage 1:**
> "Write the T-SQL scripts in sql/01_staging_schema.sql and sql/02_star_schema.sql for a SQL Server data warehouse: staging tables matching the 9 Olist CSV structures, plus a star schema with fact_order_items and five dimension tables (customer, product, seller, date, geography) as specified in this design doc. Include appropriate PK/FK constraints and surrogate keys."

**Stage 2:**
> "Generate the SSIS package logic (as BIML or a step-by-step SSDT build guide) for PKG_01 through PKG_03: extract the 9 CSVs into staging, transform and load the dimension tables with deduplication and surrogate key generation, then transform and load fact_order_items with delivery_delay_days and price_usd derived columns, joining exchange rate data from the Frankfurter API."

**Stage 3:**
> "Write the DAX measures and describe the SSAS Tabular model relationships and hierarchies specified in section 8, ready to build in SSDT."

**Stage 4:**
> "Write SQL validation tests confirming referential integrity between fact_order_items and each dimension table, and that etl_run_log row counts match source CSV row counts."

Run these as separate requests rather than one giant instruction — Antigravity handles scoped tasks more reliably.
