# Olist Brazilian E-Commerce — Data Warehouse & BI Project

> **Module:** IT3101 – Data Warehousing & Business Intelligence  
> **Dataset:** [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)  
> **Period:** 2016–2018 · ~99,441 orders / 112,650 order items

---

## Project Structure

```
DWBI Project/
├── Dataset/                          ← 9 original Olist CSV files
│   ├── olist_customers_dataset.csv
│   ├── olist_orders_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_order_payments_dataset.csv
│   ├── olist_order_reviews_dataset.csv
│   ├── olist_products_dataset.csv
│   ├── olist_sellers_dataset.csv
│   ├── olist_geolocation_dataset.csv
│   └── product_category_name_translation.csv
│
├── sql/                              ← T-SQL scripts (run in order)
│   ├── 01_staging_schema.sql         ← Creates OlistDW + stg.* tables
│   ├── 02_star_schema.sql            ← Creates dw.dim_* + dw.fact_order_items
│   ├── 03_data_mart.sql              ← Creates data mart views
│   └── 04_validation_tests.sql       ← 10 validation queries
│
├── python/                           ← Python ETL pipeline
│   ├── etl_pipeline.py              ← Master orchestrator (run this)
│   ├── 01_load_staging.py           ← CSV → stg.* (9 CSVs, 1.55M rows)
│   ├── 02_exchange_rates.py         ← Frankfurter API → stg.exchange_rates
│   ├── 02b_exchange_rates_seed.py   ← Fast historical exchange rate seeder
│   ├── 03_load_dimensions.py        ← stg.* → dw.dim_* (4 dimensions)
│   ├── 04_load_fact.py              ← stg.* → dw.fact_order_items (112,650 rows)
│   └── 05_analytical_queries.py     ← Hypothesis validation queries
│
├── ssis/                             ← SSIS Visual ETL Packages & Spec
│   ├── PKG_01_Extract_Load_Staging.dtsx
│   ├── PKG_02_Transform_Load_DimTables.dtsx
│   ├── PKG_03_Transform_Load_FactTable.dtsx
│   └── ssis_documentation.md
│
├── ssas/                             ← SSAS Tabular Model Visual Studio Solution
│   └── OlistTabularModel/
│       ├── OlistTabularModel.sln     ← Double-click to open in Visual Studio
│       ├── OlistTabularModel.smproj  ← Tabular project configuration
│       └── Model.bim                 ← Full JSON model definition
│
├── powerbi/                          ← Power BI Connections & Reports
│   ├── OlistDW_DirectQuery.pbids     ← Double-click to open Power BI in DirectQuery mode
│   └── OlistDW_Import.pbids          ← Double-click to open Power BI in Import mode
│
├── docs/
│   ├── architecture_diagram.drawio  ← Open in draw.io for system architecture & star schema
│   ├── data_catalog.md              ← Full column-level data dictionary (all 19 tables/views)
│   ├── ssas_dax_measures.md         ← SSAS Tabular + 17 DAX measures + Power BI guide
│   ├── OlistTabularModel.bim        ← Raw Tabular BIM definition
│   └── *.csv                        ← Query output CSVs (h1 through h5 evidence)
│
├── IT3101_Olist_DWBI_Project_Design.md   ← Coursework design build spec
└── IT3101 - DWBI - Assignment.pdf        ← Assignment brief
```

---

## Architecture

```
CSV Files ──┐
            ├──► SSIS / Python ETL ──► stg.* (Staging)
API (Exch.) ┘                    │
                                 ├──► dw.dim_* (Dimensions)
                                 └──► dw.fact_order_items (Fact)
                                              │
                                    dw.*_mart (Data Mart Views)
                                              │
                                    SSAS Tabular Model
                                              │
                                    Power BI Desktop (Live)
```

**3 Source Types (satisfies Task 2):**
1. **CSV files** — 9 Olist Kaggle datasets
2. **Relational DB** — SQL Server staging with PK/FK constraints
3. **REST API** — Frankfurter.app for BRL→USD exchange rates

---

## Prerequisites

| Tool | Version | Download |
|---|---|---|
| SQL Server Developer | 2019+ (2025 installed) | [microsoft.com](https://www.microsoft.com/en-us/sql-server/sql-server-downloads) |
| SSMS | Latest | [microsoft.com](https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms) |
| SSDT (Visual Studio) | Latest | [visualstudio.microsoft.com](https://visualstudio.microsoft.com/downloads/) |
| Power BI Desktop | Latest | [microsoft.com](https://powerbi.microsoft.com/downloads/) |
| Python | 3.13+ | Already installed |
| pyodbc, pandas, requests | Latest | Installed (see below) |

---

## Quick Start – Run the Full ETL

### Step 1: Install Python dependencies
```powershell
pip install pyodbc pandas requests openpyxl
```

### Step 2: Create schemas (run in SSMS or via sqlcmd)
```powershell
sqlcmd -S localhost -C -i sql\01_staging_schema.sql
sqlcmd -S localhost -C -i sql\02_star_schema.sql
```

### Step 3: Run the full Python ETL pipeline
```powershell
python python\etl_pipeline.py
```

This runs all 5 steps:
1. Loads 9 CSVs → `stg.*` staging tables (~112K fact rows)
2. Fetches exchange rates from Frankfurter API
3. Loads 4 dimension tables
4. Loads `dw.fact_order_items` with all derived columns
5. Creates data mart views

### Step 4: Validate
```powershell
sqlcmd -S localhost -C -i sql\04_validation_tests.sql
```

### Step 5: Run analytical queries (hypothesis validation)
```powershell
python python\05_analytical_queries.py
```

---

## Star Schema

**Grain:** One row per order item

```
                    ┌──────────────┐
                    │  dim_date    │
                    │  (date_key)  │
                    └──────┬───────┘
                           │
┌──────────────┐    ┌──────▼───────────────┐    ┌──────────────┐
│ dim_customer │    │  fact_order_items    │    │  dim_seller  │
│ (customer_   │◄───│                      │───►│  (seller_    │
│    key)      │    │  price_brl/usd       │    │    key)      │
└──────────────┘    │  freight_value       │    └──────────────┘
                    │  review_score        │
┌──────────────┐    │  delivery_delay_days │    ┌──────────────┐
│ dim_product  │◄───│                      │───►│dim_geography │
│ (product_key)│    │  (order_item_key PK) │    │  (geo_key)   │
└──────────────┘    └──────────────────────┘    └──────────────┘
```

---

## Business Hypotheses (Task 8)

| # | Hypothesis | Query Output |
|---|---|---|
| H1 | Delivery delays → lower review scores | `docs/h1_delay_vs_review.csv` |
| H2 | Some states have high freight-to-price ratio | `docs/h2_freight_by_state.csv` |
| H3 | November Black Friday revenue spike | `docs/h3_monthly_revenue.csv` |
| H4 | Small % of sellers cause most late deliveries | `docs/h4_late_sellers.csv` |
| H5 | Some categories have low reviews regardless of delivery | `docs/h5_category_reviews.csv` |

---

## SCD Strategy

**SCD Type 1 (Overwrite)** used for all dimensions.  
**Justification:** Dataset is a closed historical extract (2016–2018). No slowly-changing attributes need historical tracking — overwriting is correct and simplifies the ETL.

---

## ETL Run Log

After each pipeline run, check:
```sql
USE OlistDW;
SELECT * FROM dw.etl_run_log ORDER BY run_id DESC;
```

---

## SSAS & Power BI

See [`docs/ssas_dax_measures.md`](docs/ssas_dax_measures.md) for:
- SSDT project setup
- All relationship definitions
- DAX measures (revenue, delays, satisfaction, time intelligence)
- KPI definitions
- Power BI dashboard page specs (3 pages)
