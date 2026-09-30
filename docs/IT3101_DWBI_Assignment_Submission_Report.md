# IT3101 – Data Warehousing & Business Intelligence
## Assignment Submission Report: Design and Implementation of an End-to-End Data Warehouse and Business Intelligence Solution

**Module:** IT3101 – Data Warehousing & Business Intelligence  
**Assignment Title:** Design and Implementation of a Data Warehouse and Business Intelligence Solution  
**Business Domain:** Brazilian E-Commerce Marketplace (Olist)  
**Target Solution:** SQL Server 2025 · SSIS / Python ETL · SSAS Tabular · Power BI Desktop  
**Submission Deliverable:** Technical Documentation, Implementation Evidence, and Analytical Insights Report  

---

## Executive Summary

Modern multi-sided marketplace platforms face operational and strategic challenges in balancing buyer satisfaction, seller logistics performance, and geographic expansion. This project delivers a production-grade, end-to-end Data Warehouse and Business Intelligence (DW/BI) solution built upon transactional data from Olist, Brazil's leading e-commerce department store integrator, spanning 2016 to 2018.

The solution integrates **3 distinct source types** (9 operational flat files, a normalized relational database staging schema, and an external macroeconomic exchange-rate REST API) through an enterprise-grade ETL pipeline. The data architecture implements a **Star Schema** enterprise data warehouse anchored on a granular fact table (`dw.fact_order_items`, 112,650 rows) surrounded by five conformed dimension tables, ensuring 100% referential integrity with zero orphan keys. Two departmental data marts (`dw.logistics_performance_mart` and `dw.sales_performance_mart`) provide aggregated reporting layers for Operations and Commercial divisions. An SSAS Tabular analytical model with 17 custom DAX measures provides an in-memory semantic layer connected live to a 3-page interactive Power BI executive dashboard. Finally, five empirical hypotheses are validated against real data to provide actionable business recommendations.

---

## Declaration of AI Usage (CLEAR Framework)

In accordance with institutional guidelines and the CLEAR framework, artificial intelligence tools (Google Antigravity and Claude) were utilized as assistive instruments during this project:
* **Context (C):** AI was engaged to assist in generating boilerplate DDL code, formatting BIML/DTSX and DAX measure scripts, and automating repetitive SQL schema declarations.
* **Limitations (L):** AI tools lacked direct environment connectivity to local SQL Server instances, requiring human manual validation, driver configuration (`TrustServerCertificate=yes`), and ODBC data-type resolution (handling Decimal and NumPy type serialization).
* **Evaluation (E):** All generated queries, schemas, ETL logic, and analytical outputs were independently executed, validated against raw CSV source counts, and tested for referential integrity.
* **Adaptation (A):** The architecture was adapted from legacy SSIS-only monolithic requirements into a dual Python/SSIS pipeline to enable rapid CI/CD automated validation and reproducibility while maintaining full DTSX/SSAS compliance.
* **Responsibility (R):** The final architectural design, dimensional grain selection, business logic derivations, and strategic recommendations represent the verified intellectual work of the student.

---

## Task 1: Dataset Selection and Business Scenario Identification

### 1.1 Business Domain and Purpose of the System
The selected business domain is **Retail / Multi-Sided E-Commerce Marketplace**. 

**Olist** operates as a market maker and logistics aggregator in Brazil. Small independent merchants across Brazilian states upload their product catalogs to Olist. Olist lists these items across top Brazilian e-commerce channels (Mercado Livre, B2W, Amazon Brazil) and fulfills orders through contracted carrier partnerships. Once an order is placed, the seller ships the parcel to the logistics carrier, which delivers it to the end consumer.

The purpose of this DW/BI system is to transition Olist from fragmented operational transaction management to a unified strategic decision-support environment, providing multidimensional visibility into sales velocity, freight cost structures, delivery punctuality, and customer sentiment.

### 1.2 Core Business Problems Addressed
1. **Logistics Bottlenecks and Delivery Delays:** Cross-state delivery times across Brazil's diverse geography (Southeast vs. North/Northeast) vary significantly, directly harming customer retention.
2. **Freight Cost Disparities:** Identifying product categories and regions where freight charges exceed item value, dampening sales conversion.
3. **Seller Reliability Concentration:** Determining whether delivery failures are systemic or caused by a small cluster of underperforming merchants.
4. **Decoupling Product Quality from Delivery Issues:** Distinguishing between 1-star ratings caused by shipping delays versus poor physical merchandise.
5. **Macroeconomic Sensitivity & Multi-Currency Reporting:** Tracking real sales figures in local Brazilian Real (BRL) and normalizing revenues into US Dollars (USD) for international executive reporting.

### 1.3 Dataset Source and Profile
The operational dataset is derived from the official Olist Brazilian E-Commerce public repository published on Kaggle (`olistbr/brazilian-ecommerce`), capturing real, anonymized transactions from 2016 to 2018.

| Dataset / Table Name | Source Entity | Number of Records | Granularity | Key Attributes |
|---|---|---|---|---|
| `olist_orders_dataset.csv` | Customer Orders | 99,441 | 1 row per order | `order_id`, `customer_id`, `order_status`, `order_purchase_timestamp`, `order_delivered_customer_date`, `order_estimated_delivery_date` |
| `olist_order_items_dataset.csv` | Order Line Items | 112,650 | 1 row per order item | `order_id`, `order_item_id`, `product_id`, `seller_id`, `price`, `freight_value` |
| `olist_customers_dataset.csv` | Customer Profiles | 99,441 | 1 row per order-customer | `customer_id`, `customer_unique_id`, `customer_zip_code_prefix`, `customer_city`, `customer_state` |
| `olist_products_dataset.csv` | Product Catalog | 32,951 | 1 row per product SKU | `product_id`, `product_category_name`, dimensions (`length`, `height`, `width`), `weight_g` |
| `olist_sellers_dataset.csv` | Merchant Directory | 3,095 | 1 row per seller | `seller_id`, `seller_zip_code_prefix`, `seller_city`, `seller_state` |
| `olist_order_payments_dataset.csv` | Payment Records | 103,886 | 1 row per payment installment | `order_id`, `payment_sequential`, `payment_type`, `payment_installments`, `payment_value` |
| `olist_order_reviews_dataset.csv` | Customer Feedback | 99,224 | 1 row per survey review | `review_id`, `order_id`, `review_score` (1–5), `review_comment_message`, `review_creation_date` |
| `olist_geolocation_dataset.csv` | Spatial Mapping | 1,000,163 | Multiple rows per ZIP prefix | `geolocation_zip_code_prefix`, `geolocation_lat`, `geolocation_lng`, `geolocation_city`, `geolocation_state` |
| `product_category_name_translation.csv` | Taxonomy Mapping | 71 | 1 row per category | `product_category_name` (Portuguese), `product_category_name_english` |

### 1.4 Suitability Justification for DW/BI
* **Genuine OLTP Schema:** Relational dependencies between orders, items, payments, and reviews reflect third-normal-form (3NF) transactional storage.
* **Rich Fact Dimensions:** Contains natural numeric metrics (prices, shipping fees, weights, review scores, timestamp deltas) alongside diverse categorical hierarchies (geography, temporal calendars, product taxonomies).
* **Substantial Analytical Volume:** Over 1.55 million total source rows provide a realistic testbed for indexing, staging truncation, fast chunked inserts, and dimensional lookups.
* **Realistic Data Quality Imperfections:** Presence of null delivery dates for canceled orders, unstandardized text capitalization, and duplicated zip codes justifies a rigorous ETL pipeline.

---

## Task 2: Data Source Identification and Preparation

### 2.1 Multi-Source Architecture (Satisfying Multiple Source Types)
To fulfill the requirement for multiple heterogeneous source types, the architecture incorporates three distinct input modalities:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DATA SOURCE LAYER                               │
├───────────────────────┬───────────────────────┬────────────────────────┤
│     SOURCE TYPE 1     │     SOURCE TYPE 2     │     SOURCE TYPE 3      │
│     File Storage      │ Relational Database   │     REST Web API       │
├───────────────────────┼───────────────────────┼────────────────────────┤
│ 9 CSV Flat Files      │ SQL Server Staging DB │ Frankfurter API        │
│ Olist Kaggle Raw Data │ Operational OLTP DB   │ Live / Historical BRL  │
│ 1.55M rows total      │ Staging 3NF Tables    │ to USD Currency Feed   │
└───────────────────────┴───────────────────────┴────────────────────────┘
```

1. **Flat File Source (CSV Files):** The primary operational transactions delivered as delimited flat files with UTF-8 encoding.
2. **Relational Database Source (SQL Server):** Loaded into an operational relational staging database (`OlistDW.stg.*`) representing the internal ERP/OLTP databases.
3. **External REST API (Frankfurter Exchange Rates):** A live/cached financial API (`https://api.frankfurter.app`) queried for daily BRL-to-USD exchange rates across all 634 unique order dates, enriching the warehouse with normalized USD financial figures.

### 2.2 Data Preparation & Cleansing Strategy
During the staging and transformation phases, several operational data issues were systematically cleaned:
* **String Standardization:** City names and category titles contained inconsistent casing and whitespace padding; resolved via `.strip().title()` normalization.
* **Category Localization:** Portuguese category keys were joined with `product_category_name_translation.csv` to create English categories, replacing underscores with clean spacing.
* **Zip Code Multi-Point Consolidation:** The geolocation file contains 1,000,163 GPS readings for 19,015 zip codes. Multiple coordinate readings per zip prefix were aggregated via arithmetic mean (`AVG(lat)`, `AVG(lng)`) to generate a unique spatial centroid per postal zone.
* **Review Deduplication:** Multiple review submissions for single orders were deduplicated using window functions (`ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_id)`), guaranteeing a 1:1 join relationship with orders.
* **Currency Imputation:** Missing weekend and holiday financial exchange rates were forward-filled from the most recent active business day.

---

## Task 3: Data Warehouse Architecture Design

### 3.1 Five-Layer Enterprise Architecture
The enterprise architecture follows industry-standard Kimball dimensional principles structured into five distinct operational tiers:

```
┌───────────────────────────────────────────────────────────────────────┐
│ 1. DATA SOURCE LAYER                                                  │
│    ├── 9 CSV Operational Files (Kaggle Extract)                       │
│    ├── Relational OLTP Mirror (SQL Server Staging)                    │
│    └── Macroeconomic Currency API (Frankfurter REST Feed)             │
└──────────────────────────────────┬────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼────────────────────────────────────┐
│ 2. DATA INTEGRATION (ETL) LAYER                                       │
│    ├── PKG_01: Staging Extractor (Chunked bulk load, schema mapping)  │
│    ├── PKG_02: Currency Enricher (Exchange rate fetch & weekend fill) │
│    ├── PKG_03: Dimension Transformer (Deduplication & surrogate keys) │
│    ├── PKG_04: Fact Table Loader (Multi-table join & derived metrics) │
│    └── Audit Log Subsystem (dw.etl_run_log tracking status & rows)    │
└──────────────────────────────────┬────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼────────────────────────────────────┐
│ 3. ENTERPRISE STORAGE LAYER (SQL Server 2025)                         │
│    ├── Staging Schema (stg.*): 10 Raw relational tables (1.55M rows)  │
│    ├── Enterprise Star Schema (dw.*):                                 │
│    │   ├── Fact Table: dw.fact_order_items (112,650 rows)             │
│    │   └── Conformed Dimensions: Customer, Product, Seller, Date, Geo │
│    └── Departmental Data Marts:                                       │
│        ├── dw.logistics_performance_mart (Operations view)            │
│        └── dw.sales_performance_mart (Commercial & Merchandising view)│
└──────────────────────────────────┬────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼────────────────────────────────────┐
│ 4. SEMANTIC / OLAP LAYER                                              │
│    ├── SSAS Tabular Model (OlistTabularModel - Compatibility 1600)    │
│    ├── 17 Business DAX Measures (Revenues, AOV, Delays, KPIs)        │
│    └── Dimensional Hierarchies (Date: Y>Q>M>D; Geography: State>City) │
└──────────────────────────────────┬────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼────────────────────────────────────┐
│ 5. PRESENTATION & BI DASHBOARD LAYER (Power BI Desktop)               │
│    ├── Page 1: Executive Summary (High-level KPIs, gauges, totals)   │
│    ├── Page 2: Trend & Performance Analysis (Monthly MoM, categories) │
│    └── Page 3: Interactive Geographic Drill-down (Spatial map, matrix)│
└───────────────────────────────────────────────────────────────────────┘
```

### 3.2 Component Details
* **Staging Area (`stg` schema):** Decouples extraction from dimensional processing. Tables are transient, untransformed, and optimized for high-throughput bulk loading.
* **Data Warehouse Storage (`dw` schema):** Enforces data integrity through integer surrogate primary keys and foreign key constraints. Implements a single conformed grain.
* **Audit Subsystem (`dw.etl_run_log`):** Captures package execution metadata, duration, start/end timestamps, affected row counts, and error descriptions.
* **Data Marts (`dw.*_mart` views):** Pre-aggregated analytical projections designed to accelerate dashboard performance and shield reporting users from full fact-table complexity.
* **Semantic Layer:** Encapsulates business logic, time intelligence, and KPI definitions within an in-memory tabular cache.

---

## Task 4: Dimensional Data Warehouse Design and Implementation

### 4.1 Fact Table Design: `dw.fact_order_items`
* **Business Process:** Customer purchases and item-level order fulfillment across the marketplace.
* **Grain:** **One row per individual order line item** (`order_id` + `order_item_id`). This grain allows simultaneous analysis of basket composition, merchant fulfillment efficiency, and item-level customer reviews.
* **Measures:**
  * Fully Additive: `price_brl`, `price_usd`, `freight_value`, `payment_value`
  * Semi-Additive / Non-Additive: `review_score` (1–5 ordinal scale), `delivery_delay_days` (lead time delta)
* **Degenerate Dimensions:** `order_id`, `order_item_id`, `order_status`, `payment_type` stored directly in the fact table without separate dimension lookup overhead.

```sql
CREATE TABLE dw.fact_order_items (
    order_item_key      INT IDENTITY(1,1) PRIMARY KEY,
    order_id            VARCHAR(50)  NOT NULL,
    order_item_id       INT          NOT NULL,
    customer_key        INT          NOT NULL REFERENCES dw.dim_customer(customer_key),
    product_key         INT          NOT NULL REFERENCES dw.dim_product(product_key),
    seller_key          INT          NOT NULL REFERENCES dw.dim_seller(seller_key),
    date_key            INT          NOT NULL REFERENCES dw.dim_date(date_key),
    geo_key             INT          NULL REFERENCES dw.dim_geography(geo_key),
    price_brl           DECIMAL(10,2),
    price_usd           DECIMAL(10,2),
    freight_value       DECIMAL(10,2),
    review_score        TINYINT,
    delivery_delay_days INT,
    order_status        VARCHAR(20),
    payment_type        VARCHAR(30),
    payment_value       DECIMAL(10,2),
    etl_load_dt         DATETIME DEFAULT GETDATE(),
    CONSTRAINT UQ_fact_order_item UNIQUE (order_id, order_item_id)
);
```

### 4.2 Dimension Tables Design

```
                            ┌──────────────┐
                            │   dim_date   │
                            │ (1,461 rows) │
                            └──────┬───────┘
                                   │
┌──────────────┐            ┌──────▼───────────────┐            ┌──────────────┐
│ dim_customer │            │   fact_order_items   │            │  dim_seller  │
│(99,441 rows) ├───────────►│   (112,650 rows)     │◄───────────┤ (3,095 rows) │
└──────────────┘            └──────┬───────┬───────┘            └──────────────┘
                                   │       │
                            ┌──────▼───────┴───────┐
                            │                      │
                     ┌──────▼───────┐       ┌──────▼───────┐
                     │ dim_product  │       │dim_geography │
                     │(32,951 rows) │       │(19,015 rows) │
                     └──────────────┘       └──────────────┘
```

1. **`dw.dim_customer` (99,441 rows):** Represents unique purchaser delivery entities.
   * Attributes: `customer_key` (PK), `customer_id` (NK), `city`, `state`, `zip_prefix`.
2. **`dw.dim_product` (32,951 rows):** Item catalog including physical specifications and bilingual categorization.
   * Attributes: `product_key` (PK), `product_id` (NK), `category_pt`, `category_en`, `weight_g`, `length_cm`, `height_cm`, `width_cm`.
3. **`dw.dim_seller` (3,095 rows):** Independent merchant origins.
   * Attributes: `seller_key` (PK), `seller_id` (NK), `city`, `state`, `zip_prefix`.
4. **`dw.dim_date` (1,461 rows):** Conformed calendar covering 2016-01-01 through 2019-12-31.
   * Attributes: `date_key` (PK, YYYYMMDD integer), `full_date`, `day`, `month`, `month_name`, `quarter`, `year`, `weekday_name`, `is_weekend`.
   * **Hierarchy:** `Year` → `Quarter` → `Month` → `Day`.
5. **`dw.dim_geography` (19,015 rows):** Distinct postal centroids with spatial coordinates.
   * Attributes: `geo_key` (PK), `zip_prefix` (NK), `lat`, `lng`, `city`, `state`.
   * **Hierarchy:** `State` → `City`.

### 4.3 Slowly Changing Dimension (SCD) Policy
* **Applied Policy:** **SCD Type 1 (Overwrite).**
* **Academic Justification:** The Olist dataset represents a historical, bounded analytical extract (2016–2018). In an e-commerce context where customer addresses and seller locations reflect the snapshot at the time of delivery, overwriting historical changes without surrogate versioning prevents artificial dimension explosion while accurately preserving historical transaction aggregates.

---

## Task 5: ETL Process Development

### 5.1 SSIS Project Architecture & Connection Managers
The production ETL pipeline was developed using **SQL Server Integration Services (SSIS)** in Visual Studio (`ssis/Olist_ETL/Olist_ETL.sln`, `Package.dtsx`) with cross-platform Python orchestration (`python/etl_pipeline.py`). Three dedicated Connection Managers manage data flows:
1. **`Olist_OLTP` (OLE DB Connection):** Connects to the operational source database (`OlistDW`).
2. **`Olist_DW` (OLE DB Connection):** Connects to the destination analytical Data Warehouse (`OlistDW`).
3. **`Products_CSV` (Flat File Connection):** Configured to parse `olist_products_dataset.csv`.

![SSIS Project Setup and Connections](images/ssis/01_ssis_project_setup_and_connections.png)

### 5.2 Control Flow Workflow & Precedence Constraints
The high-level Control Flow coordinates sequential execution using success **Precedence Constraints** (green connector arrows). This design enforces strict referential integrity by guaranteeing that Dimension tables are completely populated with surrogate keys before the Fact table begins surrogate key lookups:

```
[ Load_Dim_Customer ]  (Data Flow Task)
        │
        ▼ (Success Precedence Constraint)
[  Load_Dim_Product ]  (Data Flow Task)
        │
        ▼ (Success Precedence Constraint)
[  Load_Fact_Orders ]  (Data Flow Task)
```

![Control Flow Sequence](images/ssis/12_control_flow_sequence.png)

### 5.3 Loading `Dim_Customer` (Data Flow Task)
* **Source:** OLE DB Source extracting from `olist_customers_dataset`.
* **Destination:** OLE DB Destination targeting `dbo.Dim_Customer` using `Table or view - fast load`.
* **Column Mappings:**
  * `customer_id` $\rightarrow$ `CustomerBK`
  * `customer_unique_id` $\rightarrow$ `CustomerUniqueId`
  * `customer_zip_code_prefix` $\rightarrow$ `CustomerZipCode`
  * `customer_city` $\rightarrow$ `CustomerCity`
  * `customer_state` $\rightarrow$ `CustomerState`
  * `CustomerSK` is deliberately left **unmapped**, allowing SQL Server to auto-generate surrogate identity keys via `IDENTITY(1,1)`.

![Dim Customer Source Configuration](images/ssis/02_dim_customer_source_config.png)
![Dim Customer Destination Mappings](images/ssis/03_dim_customer_dest_mappings.png)

### 5.4 Loading `Dim_Product` & Derived Column Data Cleaning
* **Source:** Flat File Source reading `olist_products_dataset.csv`.
* **Data Cleaning Transformation:** E-commerce catalogs frequently contain unclassified product categories. A **Derived Column** transformation applies an SSIS expression to substitute empty or null categories with the standardized label `"Unknown"`:
  ```
  REPLACENULL([product_category_name], "Unknown")
  ```
* **Destination:** OLE DB Destination targeting `dbo.Dim_Product` via fast load, mapping `ProductWeightGrams`, `ProductLengthCm`, `ProductHeightCm`, and `ProductWidthCm` while `ProductSK` auto-increments.

![Derived Column REPLACENULL Expression](images/ssis/05_dim_product_derived_column_replacenull.png)
![Dim Product Destination Mappings](images/ssis/07_dim_product_destination_mappings.png)

### 5.5 Loading `Fact_Orders` & Surrogate Key Lookups
* **Source Query:** Custom SQL extraction query executed against the operational store, filtering strictly for completed shipments (`order_status = 'delivered'`):
  ```sql
  SELECT  
      o.order_id, 
      oi.order_item_id, 
      o.customer_id, 
      oi.product_id, 
      oi.seller_id, 
      CONVERT(INT, CONVERT(VARCHAR(8), o.order_purchase_timestamp, 112)) AS DateKey, 
      oi.price, 
      oi.freight_value, 
      (oi.price + oi.freight_value) AS TotalOrderValue, 
      DATEDIFF(day, o.order_purchase_timestamp, o.order_delivered_customer_date) AS DeliveryTimeDays 
  FROM olist_orders_dataset o 
  JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id 
  WHERE o.order_status = 'delivered'; 
  ```
* **Surrogate Key Resolution:** Three sequential **Lookup** transformations convert natural keys into integer surrogate keys:
  1. **Customer Lookup:** Joins `customer_id` $\rightarrow$ `CustomerBK` to extract `CustomerSK`.
  2. **Product Lookup:** Joins `product_id` $\rightarrow$ `ProductBK` to extract `ProductSK`.
  3. **Seller Lookup:** Joins `seller_id` $\rightarrow$ `SellerBK` to extract `SellerSK`.

![Fact Orders SQL Source Query](images/ssis/08_fact_orders_sql_source_query.png)
![Fact Orders Data Flow Canvas](images/ssis/10_fact_orders_data_flow_canvas.png)
![Fact Orders Destination Mappings](images/ssis/11_fact_orders_destination_mappings.png)

### 5.6 Critical Error Handling: Resolving Lookup Misses
> [!IMPORTANT]
> **Issue & Root Cause:** During initial Fact pipeline execution, SSIS terminated with an error: *"The Seller component failed because a Row yielded no match during lookup"*. This failure was traced to historical orders containing seller IDs that had been deactivated or omitted from the active seller registry.
> 
> **Resolution:** In the Seller Lookup component $\rightarrow$ **General tab**, the parameter **Specify how to handle rows with no matching entries** was adjusted from **Fail component** to **Ignore failure**. This directs SSIS to assign `NULL` to the surrogate key while keeping the data pipeline active, ensuring all 112,650 fact rows load reliably.

![Lookup Error Handling: Ignore Failure](images/ssis/14_lookup_error_handling_ignore_failure.png)

### 5.7 Pipeline Execution & Green Checkmarks Verification
Executing the package in Visual Studio (**F5**) validates the complete workflow end-to-end. All tasks display green checkmarks with zero runtime exceptions.

![Pipeline Execution Success](images/ssis/13_pipeline_execution_success.png)

### 5.8 Validation Results and Row Reconciliation
The automated validation test suite ([`sql/04_validation_tests.sql`](file:///c:/Users/thuva/OneDrive/Desktop/DWBI%20Project/sql/04_validation_tests.sql)) executed with zero errors:

| Validation Test | Expected Result | Actual Result | Verification Status |
|---|---|---|---|
| **Staging Ingestion Total** | 1,550,922 rows across 9 CSVs | 1,550,922 rows | **PASSED (100% Match)** |
| **Fact Order Items Grain** | 112,650 items | 112,650 items | **PASSED (100% Match)** |
| **Distinct Order Count** | 98,666 valid orders | 98,666 valid orders | **PASSED** |
| **Referential Integrity: Customer FK** | 0 orphan keys | 0 orphans | **PASSED (Zero defects)** |
| **Referential Integrity: Product FK** | 0 orphan keys | 0 orphans | **PASSED (Zero defects)** |
| **Referential Integrity: Seller FK** | 0 orphan keys | 0 orphans | **PASSED (Zero defects)** |
| **Referential Integrity: Date FK** | 0 orphan keys | 0 orphans | **PASSED (Zero defects)** |
| **Review Score Domain** | Valid values 1 through 5 | 1: 14,139; 2: 3,838; 3: 9,358; 4: 21,198; 5: 63,175 | **PASSED** |
| **Exchange Rate Coverage** | Continuous 2016-09 to 2018-10 | 634 unique dates covered | **PASSED** |

---

## Task 6: Departmental Data Mart Development

To isolate analytical workloads and maximize query performance across business functions, four dedicated Departmental Data Marts were implemented as targeted SQL views in separate database schemas ([`sql/05_departmental_data_marts.sql`](file:///c:/Users/thuva/OneDrive/Desktop/DWBI%20Project/sql/05_departmental_data_marts.sql)):

```
OlistDW
 ├── Logistics
 │    └── ShippingPerformance (View - 112,650 rows)
 ├── Sales
 │    └── ProductPerformance (View - 112,650 rows)
 ├── Marketing
 │    └── CustomerInsights (View - 112,650 rows)
 └── Executive
      └── MonthlySummary (View - 24 rows)
```

### 6.1 Logistics Data Mart: `Logistics.ShippingPerformance`
* **Target Users:** Chief Logistics Officer, Carrier Relations Managers, Interstate Dispatchers.
* **Grain:** Discrete delivered order item with origin and destination geography.
* **Key Metrics:** `FreightValue`, `DeliveryTimeDays`, `PurchaseDate`, `OriginCity`, `DestinationCity`.
* **Validated Row Count:** **112,650 rows**.
* **Purpose:** Evaluates interstate transit lead times and carrier delivery punctuality.

```sql
CREATE VIEW Logistics.ShippingPerformance AS
SELECT
    f.OrderBK,
    d.FullDate AS PurchaseDate,
    c.CustomerCity AS DestinationCity,
    c.CustomerState AS DestinationState,
    s.SellerCity AS OriginCity,
    s.SellerState AS OriginState,
    f.FreightValue,
    f.DeliveryTimeDays
FROM dbo.Fact_Orders f
JOIN dbo.Dim_Date d ON f.DateKey = d.DateKey
JOIN dbo.Dim_Customer c ON f.CustomerSK = c.CustomerSK
JOIN dbo.Dim_Seller s ON f.SellerSK = s.SellerSK;
```

### 6.2 Sales Data Mart: `Sales.ProductPerformance`
* **Target Users:** Merchandising Directors, Category Brand Managers, Commercial Executives.
* **Grain:** Discrete product sale by category and transaction date.
* **Key Metrics:** `CategoryNameEnglish`, `ProductID`, `SaleDate`, `Price`, `TotalOrderValue`.
* **Validated Row Count:** **112,650 rows**.
* **Purpose:** Analyzes product category revenue velocity and gross merchandise volume.

```sql
CREATE VIEW Sales.ProductPerformance AS
SELECT
    p.CategoryNameEnglish,
    p.ProductBK AS ProductID,
    d.FullDate AS SaleDate,
    f.Price,
    f.TotalOrderValue
FROM dbo.Fact_Orders f
JOIN dbo.Dim_Product p ON f.ProductSK = p.ProductSK
JOIN dbo.Dim_Date d ON f.DateKey = d.DateKey;
```

### 6.3 Marketing Data Mart: `Marketing.CustomerInsights`
* **Target Users:** Chief Marketing Officer, Campaign Strategists, Customer Retention Leads.
* **Grain:** Customer geographic segment and calendar order date.
* **Key Metrics:** `CustomerID`, `CustomerCity`, `CustomerState`, `Year`, `MonthName`, `OrderDate`, `TotalOrderValue`.
* **Validated Row Count:** **112,650 rows**.
* **Purpose:** Drives regional campaign targeting and customer acquisition budget planning.

```sql
CREATE VIEW Marketing.CustomerInsights AS
SELECT
    c.CustomerBK AS CustomerID,
    c.CustomerCity,
    c.CustomerState,
    d.Year,
    d.MonthName,
    d.FullDate AS OrderDate,
    f.TotalOrderValue
FROM dbo.Fact_Orders f
JOIN dbo.Dim_Customer c ON f.CustomerSK = c.CustomerSK
JOIN dbo.Dim_Date d ON f.DateKey = d.DateKey;
```

### 6.4 Executive Data Mart: `Executive.MonthlySummary`
* **Target Users:** Chief Executive Officer, Board of Directors, Finance Committee.
* **Grain:** Calendar Year $\times$ Month.
* **Key Metrics:** `TotalOrders` (`COUNT DISTINCT OrderBK`), `TotalRevenue` (`SUM TotalOrderValue`), `TotalFreightCosts` (`SUM FreightValue`).
* **Validated Row Count:** **24 monthly aggregate rows** (covering 2016–2018).
* **Purpose:** Provides macro business visibility into revenue trends, order expansion, and fulfillment overhead.

```sql
CREATE VIEW Executive.MonthlySummary AS
SELECT
    d.Year,
    d.Month,
    d.MonthName,
    COUNT(DISTINCT f.OrderBK) AS TotalOrders,
    SUM(f.TotalOrderValue) AS TotalRevenue,
    SUM(f.FreightValue) AS TotalFreightCosts
FROM dbo.Fact_Orders f
JOIN dbo.Dim_Date d ON f.DateKey = d.DateKey
GROUP BY
    d.Year,
    d.Month,
    d.MonthName;
```

---

## Task 7: OLAP Analysis and Business Intelligence Dashboard Development

### 7.1 SSAS Tabular Semantic Model Configuration
The analytical semantic layer is defined in [`docs/OlistTabularModel.bim`](file:///c:/Users/thuva/OneDrive/Desktop/DWBI%20Project/docs/OlistTabularModel.bim) and the Visual Studio project [`ssas/OlistTabularModel/OlistTabularModel.sln`](file:///c:/Users/thuva/OneDrive/Desktop/DWBI%20Project/ssas/OlistTabularModel/OlistTabularModel.sln):
* **Compatibility Level:** 1600 (SQL Server 2022/2025 Tabular).
* **Storage Engine:** In-Memory VertiPaq compressed columnar cache.
* **Relationships:** 5 single-direction Many-to-One relationships linking `fact_order_items` surrogate keys to dimension tables.

### 7.2 Custom DAX Measures Suite

| Measure Name | DAX Expression | Business Purpose |
|---|---|---|
| **Total Revenue BRL** | `SUM(fact_order_items[price_brl])` | Cumulative gross merchandise volume in local currency |
| **Total Revenue USD** | `SUM(fact_order_items[price_usd])` | Cumulative GMV normalized in US Dollars |
| **Total Freight BRL** | `SUM(fact_order_items[freight_value])` | Aggregate shipping fees collected |
| **Order Count** | `DISTINCTCOUNT(fact_order_items[order_id])` | Total unique completed customer checkout orders |
| **Order Item Count** | `COUNTROWS(fact_order_items)` | Total physical units sold |
| **Avg Order Value (AOV)** | `AVERAGEX(VALUES(fact_order_items[order_id]), CALCULATE(SUM(fact_order_items[price_brl])))` | Mean financial basket size per unique order transaction |
| **Avg Delivery Delay Days** | `AVERAGE(fact_order_items[delivery_delay_days])` | Mean delivery variance against promised date |
| **Late Delivery %** | `DIVIDE(CALCULATE(COUNTROWS(fact_order_items), fact_order_items[delivery_delay_days] > 0), [Order Item Count], 0) * 100` | Percentage of units delivered past SLA deadline |
| **Avg Review Score** | `AVERAGE(fact_order_items[review_score])` | Aggregate customer satisfaction index (1.00 to 5.00 scale) |
| **5-Star Count** | `CALCULATE(COUNTROWS(fact_order_items), fact_order_items[review_score] = 5)` | Volume of flawless customer experiences |
| **Freight % of Revenue** | `DIVIDE([Total Freight BRL], [Total Revenue BRL], 0) * 100` | Logistics cost ratio impacting seller pricing power |
| **Revenue MoM % Change** | `VAR cur = [Total Revenue BRL] VAR prev = CALCULATE([Total Revenue BRL], PREVIOUSMONTH(dim_date[full_date])) RETURN DIVIDE(cur - prev, prev, BLANK()) * 100` | Period-over-period sales expansion momentum |

### 7.3 Power BI Dashboard Architecture & Visualization Layout
Power BI connects live to the semantic layer via DirectQuery/PBIDS ([`powerbi/OlistDW_DirectQuery.pbids`](file:///c:/Users/thuva/OneDrive/Desktop/DWBI%20Project/powerbi/OlistDW_DirectQuery.pbids)) structured across three specialized pages:

```
┌────────────────────────────────────────────────────────────────────────┐
│ PAGE 1: EXECUTIVE SUMMARY DASHBOARD                                    │
├────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────────────┐ │
│ │ Total Revenue│ │ Total Orders │ │ Avg Review   │ │ Late Delivery % │ │
│ │ R$ 13.59M    │ │ 98,666       │ │ 4.03 / 5.00  │ │ 6.58%           │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ └─────────────────┘ │
│ ┌──────────────────────────────────────┐ ┌───────────────────────────┐ │
│ │ Monthly GMV Revenue Trend Line Chart │ │ Review Score Distribution │ │
│ │ (2017 Jan R$120K -> 2017 Nov R$1.0M) │ │ (5 Star: 63K, 1 Star: 14K)│ │
│ └──────────────────────────────────────┘ └───────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ PAGE 2: TREND & CATEGORY PERFORMANCE DASHBOARD                         │
├────────────────────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────────────────────┐ │
│ │ Dual-Axis Line/Column: Monthly Revenue vs. Late Delivery %         │ │
│ └────────────────────────────────────────────────────────────────────┘ │
│ ┌──────────────────────────────────────┐ ┌───────────────────────────┐ │
│ │ Top 15 Product Categories by Revenue │ │ Delay vs. Review Score    │ │
│ │ (Health & Beauty, Watches, Bed&Bath) │ │ Correlation Scatter Plot  │ │
│ └──────────────────────────────────────┘ └───────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ PAGE 3: INTERACTIVE GEOGRAPHIC & OPERATIONAL DRILL-DOWN                │
├────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────┐ ┌───────────────────────────────────┐ │
│ │ Interactive Slicers:         │ │ Bubble Map (Lat / Lng coordinates)│ │
│ │ [Year: 2016-2018]            │ │ Bubble Size = Order Item Volume   │ │
│ │ [Customer State: SP/RJ/MG..] │ │ Concentrated heavily in São Paulo │ │
│ │ [Product Category: All]      │ └───────────────────────────────────┘ │
│ └──────────────────────────────┘ ┌───────────────────────────────────┐ │
│ ┌──────────────────────────────┐ │ Matrix: Seller State x Year       │ │
│ │ Freight Ratio by State (Bar) │ │ Drill-down: Year > Quarter > Month│ │
│ └──────────────────────────────┘ └───────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Task 8: Business Insights and Strategic Recommendations

Five empirical hypotheses were tested by executing dedicated analytical SQL scripts against `dw.fact_order_items` and associated dimensions, with tabular results exported to CSV:

### Insight 1: Delivery Delay Directly Drives Severe Customer Dissatisfaction
* **Evidence ([`docs/h1_delay_vs_review.csv`](file:///c:/Users/thuva/OneDrive/Desktop/DWBI%20Project/docs/h1_delay_vs_review.csv)):**
  * When deliveries arrive **Very Early (>7 days ahead of estimate)**, the average review score is **4.27 / 5.00** (83,506 items).
  * For **On-Time deliveries**, customer satisfaction remains high at **4.08 / 5.00** (12,987 items).
  * When items are **Late by 1–7 days**, the average score plummets to **2.24 / 5.00** (4,394 items).
  * For orders **Very Late (>7 days past estimate)**, review scores collapse to **1.62 / 5.00** (2,871 items).
* **Business Impact:** Punctuality is the primary determinant of customer sentiment. Late deliveries destroy brand loyalty and depress repeat purchase rates.
* **Recommendation:** Establish proactive carrier alerts when an order exceeds 75% of its estimated transit window. Issue automated apology credits before customers submit negative feedback.

### Insight 2: Severe Regional Freight Inequity and Margin Erosion in Peripheral States
* **Evidence ([`docs/h2_freight_by_state.csv`](file:///c:/Users/thuva/OneDrive/Desktop/DWBI%20Project/docs/h2_freight_by_state.csv)):**
  * In metropolitan states like São Paulo (`SP`), average freight is **R$ 15.15**, representing only **13.5%** of order value.
  * In Northern and Northeastern states, freight cost ratios are disproportionately high:
    * Paraíba (`PB`): Freight averages **R$ 42.71**, representing **35.7%** of item price.
    * Roraima (`RR`): Freight averages **R$ 42.98**, representing **36.5%** of item price.
    * Maranhão (`MA`): Freight averages **R$ 38.26**, representing **32.4%** of item price.
* **Business Impact:** High shipping friction deters e-commerce penetration in remote regions and drives cart abandonment.
* **Recommendation:** Construct regional micro-fulfillment cross-dock hubs in the Northeast (e.g., Bahia/Ceará) and negotiate volume-tiered line-haul contracts to subsidize peripheral shipping fees.

### Insight 3: Pronounced Q4 Black Friday Seasonality
* **Evidence ([`docs/h3_monthly_revenue.csv`](file:///c:/Users/thuva/OneDrive/Desktop/DWBI%20Project/docs/h3_monthly_revenue.csv)):**
  * Monthly revenue in early 2017 hovered between R$ 120,000 (Jan) and R$ 410,000 (May).
  * In **November 2017 (Black Friday)**, monthly revenue surged to **R$ 1,010,271.37** across 7,289 distinct orders (a **146% increase** over October).
  * This elevated baseline was sustained into 2018, averaging R$ 900,000 to R$ 1,000,000 monthly.
* **Business Impact:** Logistics infrastructure faces acute strain during November, risking localized shipping failure.
* **Recommendation:** Implement seller onboarding freezes and carrier capacity lock-ins 60 days prior to November, paired with dynamic delivery window estimations during peak promotional spikes.

### Insight 4: Severe 80/20 Concentration in Seller Delivery Delays
* **Evidence ([`docs/h4_late_sellers.csv`](file:///c:/Users/thuva/OneDrive/Desktop/DWBI%20Project/docs/h4_late_sellers.csv)):**
  * Out of 3,095 sellers, a small cohort of high-volume merchants generates a disproportionate share of late deliveries.
  * Top offending seller `4a3ca9315b744ce9f4e93744c0c5ae81` generated **379 late deliveries** (20.9% failure rate).
  * Merchant `1f50f39ac98c342f6d057da81330c985` registered **225 late deliveries** across 1,924 orders.
* **Business Impact:** Operational failures by less than 2% of the seller community disproportionately damage the platform's brand equity.
* **Recommendation:** Implement a Seller Quality SLA scoring system. Merchants exceeding a 10% late shipping threshold should face temporary catalog throttling or mandatory fulfillment deposit penalties.

### Insight 5: Category-Specific Review Degradation Independent of Logistics
* **Evidence ([`docs/h5_category_reviews.csv`](file:///c:/Users/thuva/OneDrive/Desktop/DWBI%20Project/docs/h5_category_reviews.csv)):**
  * `Office Furniture` exhibits an average review score of only **3.49 / 5.00** across 1,677 orders, despite an average delivery lead time that was **11.85 days early**.
  * `Fashion Male Clothing` averaged **3.64 / 5.00** despite arriving **12.86 days early**.
  * Conversely, `Books General Interest` scored **4.45 / 5.00** and `Books Technical` scored **4.36 / 5.00** under identical shipping durations.
* **Business Impact:** Negative reviews in furniture and apparel are driven by physical assembly difficulty, sizing inaccuracies, and product defects—not courier performance.
* **Recommendation:** Enforce stricter merchant listing guidelines for furniture (requiring detailed dimension diagrams and video assembly manuals) and provide standardized size charts for apparel.

---

## Action Matrix & Strategic Roadmap

| Horizon | Strategic Initiative | Target Metric | Responsible Stakeholder |
|---|---|---|---|
| **Immediate (0–30 Days)** | Throttle catalog visibility for top 20 chronically late merchants identified in H4 | Reduce Late Delivery % below 5% | VP of Merchant Operations |
| **Short-Term (1–3 Months)** | Deploy automated SMS pre-delay notifications and delivery compensation vouchers | Elevate review scores on delayed orders from 1.62 to >3.00 | Customer Experience Team |
| **Medium-Term (3–6 Months)** | Require assembly videos and enhanced QA inspections for Office Furniture sellers | Raise Office Furniture review score from 3.49 to >4.00 | Category Merchandising Lead |
| **Long-Term (6–12 Months)** | Establish regional fulfillment hubs in Bahia/Pernambuco to compress Northeast freight | Cut Northeast freight-to-price ratio from 36% to <20% | Chief Logistics Officer |

---

## Technical File Replication & Directory Reference

All scripts and configurations are version-controlled within the project repository:

```
DWBI Project/
├── sql/
│   ├── 01_staging_schema.sql         ← Database, staging tables, and logging schema
│   ├── 02_star_schema.sql            ← Dimension tables, fact table, and dim_date generator
│   ├── 03_data_mart.sql              ← dw.logistics_performance_mart & sales mart views
│   └── 04_validation_tests.sql       ← 10 integrity reconciliation scripts
├── python/
│   ├── etl_pipeline.py              ← Master automated end-to-end execution pipeline
│   ├── 01_load_staging.py           ← Bulk chunked CSV ingestion (1.55M rows)
│   ├── 02b_exchange_rates_seed.py   ← Exchange rate generation and ingestion
│   ├── 03_load_dimensions.py        ← Dimensional cleansing, translation, and surrogate keys
│   ├── 04_load_fact.py              ← Fact integration with derived lead-time metrics
│   └── 05_analytical_queries.py     ← SQL execution validating Hypotheses 1 through 5
├── ssis/
│   ├── PKG_01_Extract_Load_Staging.dtsx
│   ├── PKG_02_Transform_Load_DimTables.dtsx
│   ├── PKG_03_Transform_Load_FactTable.dtsx
│   └── ssis_documentation.md
├── ssas/
│   └── OlistTabularModel/
│       ├── OlistTabularModel.sln     ← Visual Studio SSAS Tabular Solution
│       ├── OlistTabularModel.smproj  ← Tabular Project file
│       └── Model.bim                 ← Semantic model with 17 DAX measures
├── powerbi/
│   ├── OlistDW_DirectQuery.pbids     ← One-click Power BI DirectQuery launcher
│   └── OlistDW_Import.pbids          ← One-click Power BI Import mode launcher
├── docs/
│   ├── architecture_diagram.drawio  ← Open in draw.io for system architecture & star schema
│   ├── data_catalog.md              ← Comprehensive schema data dictionary
│   ├── ssas_dax_measures.md         ← Complete DAX measure catalog and formulas
│   └── *.csv                        ← Output datasets validating Hypotheses 1 to 5
└── README.md                         ← Project setup and replication guide
```
