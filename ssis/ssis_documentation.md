# SSIS ETL Package Design & Documentation

> **Module:** IT3101 – Data Warehousing & Business Intelligence  
> **Coursework Component:** Task 5 – Visual ETL Pipeline

---

## 1. Package Architecture Overview

The ETL workflow is designed into **3 modular SSIS packages**, ensuring separation of concerns, independent testability, and clear audit logging:

```
┌────────────────────────────────────────────────────────┐
│ PKG_01_Extract_Load_Staging.dtsx                       │
│ ├─ Flat File Sources (9 Olist CSVs)                   │
│ ├─ OLE DB Destination -> stg.* tables                 │
│ ├─ Script Task -> Frankfurter / Historical Exch Rates  │
│ └─ Execute SQL Task -> Log to dw.etl_run_log           │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ PKG_02_Transform_Load_DimTables.dtsx                   │
│ ├─ Execute SQL -> Clear existing fact & dimension keys │
│ ├─ Data Flow: stg.customers -> dw.dim_customer         │
│ ├─ Data Flow: stg.products + pc -> dw.dim_product      │
│ ├─ Data Flow: stg.sellers -> dw.dim_seller             │
│ ├─ Data Flow: stg.geolocation (Agg) -> dw.dim_geography│
│ └─ Execute SQL Task -> Log to dw.etl_run_log           │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ PKG_03_Transform_Load_FactTable.dtsx                   │
│ ├─ OLE DB Source: Join stg.order_items & stg.orders    │
│ ├─ Derived Column: delivery_delay_days, date_key       │
│ ├─ Lookup Transforms: Customer, Product, Seller, Geo   │
│ ├─ Merge Join / Lookup: stg.exchange_rates (price_usd) │
│ ├─ OLE DB Destination -> dw.fact_order_items           │
│ └─ Execute SQL Task -> Log to dw.etl_run_log           │
└────────────────────────────────────────────────────────┘
```

---

## 2. Package Breakdown

### PKG_01: Extract & Load Staging (`PKG_01_Extract_Load_Staging.dtsx`)
- **Connection Managers:**
  - `FlatFile_Customers`, `FlatFile_Orders`, `FlatFile_OrderItems`, etc.
  - `OLEDB_OlistDW`: Target SQL Server (`localhost`, database `OlistDW`)
- **Control Flow:**
  1. `SQL_Log_Start`: Inserts start timestamp into `dw.etl_run_log`.
  2. `DFT_Load_Customers` ... `DFT_Load_Geolocation` (9 parallel/sequential data flows).
  3. `Script_Fetch_ExchangeRates`: Pulls rates from Frankfurter API or seeds quarterly historical rates.
  4. `SQL_Log_End`: Updates status to 'SUCCESS' and records row counts.

### PKG_02: Transform & Load Dimension Tables (`PKG_02_Transform_Load_DimTables.dtsx`)
- **Transforms Used:**
  - **Data Conversion Transform:** Enforces UTF-8 strings, trimmed characters, and prevents float inference on text ID columns.
  - **Sort & Aggregate Transform:** Deduplicates customers, sellers, products, and computes `AVG(lat)` and `AVG(lng)` for `dim_geography`.
  - **Derived Column Transform:** Converts Portuguese names and translates to English title-casing.
  - **SCD Strategy:** SCD Type 1 (truncate/delete and reload) with logging.

### PKG_03: Transform & Load Fact Table (`PKG_03_Transform_Load_FactTable.dtsx`)
- **Grain:** One row per order item (112,650 rows).
- **Transformations:**
  - `delivery_delay_days`: `DATEDIFF("dd", order_estimated_delivery_date, order_delivered_customer_date)`
  - `price_usd`: `ROUND(price_brl * usd_per_brl, 2)`
  - **Lookup Transformations:**
    - `LKP_Customer`: Natural key `customer_id` -> Surrogate `customer_key`
    - `LKP_Product`: Natural key `product_id` -> Surrogate `product_key`
    - `LKP_Seller`: Natural key `seller_id` -> Surrogate `seller_key`
    - `LKP_Geography`: Zip code prefix -> Surrogate `geo_key`
- **Output:** 112,650 rows loaded with zero orphan foreign keys.

---

## 3. Python vs SSIS Parity

In this project, complete automated execution is provided via both:
1. **Python Pipeline (`python/etl_pipeline.py`)**: Runs directly on any developer machine without requiring full Visual Studio SSIS designer licenses, executing the exact same 3-stage logic in under 60 seconds.
2. **SSIS Package Design Spec**: Full structural specification, connection configurations, and schema targets for deployment within Visual Studio SSDT.
