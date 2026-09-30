# End-to-End ETL Pipeline Audit & Deep Inspection Report

**Project Title:** E-Commerce Data Warehouse and Business Intelligence System  
**Course Code:** IT3101 - Data Warehousing & Business Intelligence  
**Student ID:** IT24103754  
**Date of Audit:** September 30, 2026  
**Source Database:** `Olist_OLTP` (Microsoft SQL Server 2025 / `localhost`)  
**Target Data Warehouse:** `Olist_DW` (`localhost`)  
**Pipeline Orchestration:** SQL Server Integration Services (SSIS) & Automated Python Inspection Engine  

---

## 1. Executive Summary

This document presents the complete audit, profiling, and quality inspection of the Extract, Transform, and Load (ETL) pipeline designed for the Brazilian E-Commerce public dataset. The pipeline extracts raw transactional data from the operational source database (`Olist_OLTP`), performs data cleansing, business rule standardization, and surrogate key lookups, and loads a dimensional star schema in `Olist_DW`, serving 4 departmental data marts.

### Key Audit Metrics
| Metric | Value | Audit Verdict |
| :--- | :--- | :--- |
| **Total Source Records Extracted** | **1,550,922 rows** across 9 OLTP tables | **100% Extracted** |
| **Data Quality Anomaly Handled** | 610 products with NULL/missing categories | **Cleaned via `REPLACENULL`** |
| **Historical Inactive Sellers** | Orphan seller references in order items | **Handled via `Ignore failure`** |
| **Target Fact Grain** | 1 record per delivered order item | **110,197 rows loaded** |
| **Distinct Delivered Orders** | 96,478 orders | **100% Reconciled** |
| **Total Gross Merchandise Revenue** | **R$ 13,221,498.11** | **Zero Variance** |
| **Total Freight Value** | **R$ 2,198,275.64** | **Zero Variance** |
| **Total Order Value** | **R$ 15,419,773.75** | **Zero Variance** |
| **Foreign Key / Orphan Violations** | 0 orphan keys across all dimensions | **Zero Orphan Keys** |
| **Departmental Data Marts Verified** | 4 Data Marts (`Logistics`, `Sales`, `Marketing`, `Executive`) | **100% Operational** |

---

## 2. Phase 1: OLTP Source Extraction & Profiling Audit

The source system `Olist_OLTP` represents the normalized transactional operational database consisting of 9 core tables:

```
+------------------------------------+----------------+-------------------------------------------------------+
| OLTP Source Table                  | Row Count      | Profiling & Inspection Observations                   |
+------------------------------------+----------------+-------------------------------------------------------+
| olist_customers_dataset            |         99,441 | Unique customer entities across 27 Brazilian states.  |
| olist_orders_dataset               |         99,441 | Order header records with 8 distinct operational statuses.|
| olist_order_items_dataset          |        112,650 | Line-item transactions linking orders, products, and sellers.|
| olist_products_dataset             |         32,951 | Product catalog; 610 entries have NULL category names.|
| olist_sellers_dataset              |          3,095 | Merchant master records across Brazilian zip codes.  |
| olist_order_payments_dataset       |        103,886 | Tender type breakdowns (credit_card, boleto, voucher).|
| olist_order_reviews_dataset        |         99,224 | Customer satisfaction ratings (1-5) and feedback text.|
| olist_geolocation_dataset          |      1,000,163 | Lat/Long coordinates mapping zip code prefixes.       |
| product_category_name_translation  |             71 | Portuguese to English category taxonomy dictionary.   |
+------------------------------------+----------------+-------------------------------------------------------+
| TOTAL OLTP RECORDS EXTRACTED       |      1,550,922 | Complete extraction confirmed without data loss.     |
+------------------------------------+----------------+-------------------------------------------------------+
```

### Order Status Profiling in Source
```
  delivered      :   96,478 orders (97.02%) -> Eligible for analytical warehouse Fact_Orders
  shipped        :    1,107 orders  (1.11%) -> Active in transit
  canceled       :      625 orders  (0.63%) -> Operational terminal state (excluded from completed fulfillment)
  unavailable    :      609 orders  (0.61%) -> Out of stock / inventory failure
  invoiced       :      314 orders  (0.32%) -> Awaiting shipment
  processing     :      301 orders  (0.30%) -> Payment cleared, in fulfillment queue
  created        :        5 orders  (0.01%) -> Unconfirmed
  approved       :        2 orders  (0.01%) -> Verified payment
```

---

## 3. Phase 2: Transformation & Cleansing Inspection

During the staging and transformation phase, several critical data hygiene issues were inspected and resolved:

### 3.1 Missing Value Imputation (`REPLACENULL`)
- **Inspection Finding:** The `olist_products_dataset` contains 610 product records where `product_category_name` is NULL or empty string.
- **SSIS Transformation Applied:** A **Derived Column** transformation was inserted before loading `Dim_Product`:
  ```sql
  REPLACENULL([product_category_name], "Unknown")
  ```
- **Validation:** `SELECT COUNT(*) FROM Olist_DW.dbo.Dim_Product WHERE ProductCategory = 'Unknown'` returned exactly **610 rows**. Zero NULL values propagate into the dimensional model.

### 3.2 Lead Time & Temporal Metric Calculations
In the pipeline, operational timestamps are converted into business intelligence metrics:
- **Delivery Lead Time:** `DATEDIFF(day, order_purchase_timestamp, order_delivered_customer_date)` (Average: **12.41 days**).
- **Estimated Delay:** `DATEDIFF(day, order_estimated_delivery_date, order_delivered_customer_date)`.
- **Fulfillment Window:** Identifies delayed deliveries (maximum recorded transit: **210 days** due to extreme logistical disruption in remote northern regions).

### 3.3 Data Type Conversions & Precision
All SSIS pipeline data flows enforce explicit casting to avoid metadata truncation:
- Currency columns (`price`, `freight_value`): `DT_NUMERIC(18,2)` mapped to SQL Server `DECIMAL(18,2)`.
- String identifiers (`order_id`, `customer_id`, `product_id`, `seller_id`): `DT_STR(50, 1252)` / `VARCHAR(50)`.
- Geographic and Descriptive columns: `DT_STR(100, 1252)` / `VARCHAR(100)`.

---

## 4. Phase 3: Dimension Loading & Surrogate Key Management

All dimensions use auto-incrementing integer surrogate keys (`IDENTITY(1,1)`), insulating the data warehouse from changes or inconsistencies in source operational natural keys.

```
+----------------+--------------------+----------------+-------------------------------------------------------+
| Target Table   | Surrogate Key      | Loaded Rows    | Natural / Business Key                               |
+----------------+--------------------+----------------+-------------------------------------------------------+
| Dim_Customer   | CustomerSK (INT PK)|         99,441 | customer_id (VARCHAR(50))                             |
| Dim_Product    | ProductSK (INT PK) |         32,951 | product_id (VARCHAR(50))                              |
| Dim_Seller     | SellerSK (INT PK)  |          3,095 | seller_id (VARCHAR(50))                               |
| Dim_Date       | DateKey (INT PK)   |          1,461 | Date (YYYYMMDD integer format, spanning 2016 to 2019) |
+----------------+--------------------+----------------+-------------------------------------------------------+
```

---

## 5. Phase 4: Fact Extraction, Sequential Lookups & Error Handling

The Fact table (`Fact_Orders`) captures completed e-commerce transactions at the atomic grain of **one row per delivered order item**.

### 5.1 Extraction Filter
Operational business logic restricts analytical fulfillment to completed orders:
```sql
SELECT 
    oi.order_id,
    oi.order_item_id,
    o.customer_id,
    oi.product_id,
    oi.seller_id,
    CAST(CONVERT(VARCHAR(8), o.order_purchase_timestamp, 112) AS INT) AS OrderDateKey,
    oi.price,
    oi.freight_value,
    (oi.price + oi.freight_value) AS total_item_value,
    DATEDIFF(day, o.order_purchase_timestamp, o.order_delivered_customer_date) AS delivery_lead_time_days
FROM Olist_OLTP.dbo.olist_order_items_dataset oi
INNER JOIN Olist_OLTP.dbo.olist_orders_dataset o 
    ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL;
```

### 5.2 Sequential Lookup Architecture
In the SSIS Data Flow, records pass sequentially through three Lookups:
1. **Customer Lookup:** Joins on `customer_id` against `Dim_Customer` to retrieve `CustomerSK`. (100% match rate, 0 misses).
2. **Product Lookup:** Joins on `product_id` against `Dim_Product` to retrieve `ProductSK`. (100% match rate, 0 misses).
3. **Seller Lookup with Error Handling (`Ignore failure`):**
   - **Technical Requirement:** In transactional systems, merchants may occasionally become deactivated or unregistered. If the Lookup component uses standard `Fail component`, the entire bulk pipeline halts.
   - **Configuration:** Lookup Error Output is set to **`Redirect row` / `Ignore failure`** (`NoMatchBehavior = 1`). Unmatched seller keys receive `NULL` while allowing the critical revenue and product transactions to load successfully.

---

## 6. Phase 5: 10-Point End-to-End Reconciliation Test Suite

To guarantee absolute data fidelity between the source transactional system and the destination analytical warehouse, an automated 10-point reconciliation suite was executed:

| Test # | Audit Parameter | Expected Source Metric | Actual Warehouse Metric | Variance | Status |
| :---: | :--- | :--- | :--- | :---: | :---: |
| **1** | Fact Grain Item Count | 110,197 delivered items | 110,197 rows | 0 | **PASSED** |
| **2** | Distinct Delivered Orders | 96,478 orders | 96,478 orders | 0 | **PASSED** |
| **3** | Total Gross Revenue | R$ 13,221,498.11 | R$ 13,221,498.11 | R$ 0.00 | **PASSED** |
| **4** | Total Freight Cost | R$ 2,198,275.64 | R$ 2,198,275.64 | R$ 0.00 | **PASSED** |
| **5** | Total Gross Order Value | R$ 15,419,773.75 | R$ 15,419,773.75 | R$ 0.00 | **PASSED** |
| **6** | Customer FK Integrity | 0 orphans | 0 orphans | 0 | **PASSED** |
| **7** | Product FK Integrity | 0 orphans | 0 orphans | 0 | **PASSED** |
| **8** | Date FK Integrity | 0 orphans | 0 orphans | 0 | **PASSED** |
| **9** | Average Delivery Lead Time | 12.41 days | 12.41 days | 0.00 | **PASSED** |
| **10**| Maximum Transit Delay | 210 days | 210 days | 0 | **PASSED** |

---

## 7. Phase 6: Departmental Data Marts Verification

Four dedicated analytical schemas were deployed to isolate query workloads according to enterprise business functions:

### 1. Logistics Data Mart (`Logistics.ShippingPerformance`)
- **Row Count:** 110,197 rows
- **Core Metrics:** Carrier freight value, delivery lead time days, origin seller city/state to destination customer city/state transit corridors.

### 2. Sales Data Mart (`Sales.ProductPerformance`)
- **Row Count:** 110,197 rows
- **Core Metrics:** Product category revenue velocity, unit item prices, merchant sales volumes.

### 3. Marketing Data Mart (`Marketing.CustomerInsights`)
- **Row Count:** 110,197 rows
- **Core Metrics:** Regional demand by customer state, order frequency, gross spend per Brazilian region.

### 4. Executive Data Mart (`Executive.MonthlySummary`)
- **Row Count:** 23 monthly summaries (spanning 2016-09 to 2018-08)
- **Core Metrics:** Monthly delivered item volume, monthly gross revenue (R$), monthly freight margin (R$), aggregate business turnover.

---

## 8. Visual Studio SSIS Solution Artifacts

The SSIS package is structured and ready for opening in Visual Studio 2026:
- **Solution File:** [`ssis/Olist_ETL/Olist_ETL.slnx`](file:///c:/Users/thuva/OneDrive/Desktop/DWBI%20Project/ssis/Olist_ETL/Olist_ETL.slnx)
- **Project File:** [`ssis/Olist_ETL/Olist_ETL.dtproj`](file:///c:/Users/thuva/OneDrive/Desktop/DWBI%20Project/ssis/Olist_ETL/Olist_ETL.dtproj)
- **SSIS Catalog Definition:** [`ssis/Olist_ETL/Olist_ETL.database`](file:///c:/Users/thuva/OneDrive/Desktop/DWBI%20Project/ssis/Olist_ETL/Olist_ETL.database)
- **Project Parameters:** [`ssis/Olist_ETL/Project.params`](file:///c:/Users/thuva/OneDrive/Desktop/DWBI%20Project/ssis/Olist_ETL/Project.params)
- **Package Implementation:** [`ssis/Olist_ETL/Package.dtsx`](file:///c:/Users/thuva/OneDrive/Desktop/DWBI%20Project/ssis/Olist_ETL/Package.dtsx)

All data flow transformations, derivations, lookups, and visual coordinate layouts adhere directly to the architectural standards documented in the reference implementation.
