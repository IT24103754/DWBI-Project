# Olist DWBI – Data Catalog

> IT3101 · Data Warehouse & Business Intelligence Project  
> Dataset: Brazilian E-Commerce (Olist) · Period: 2016–2018

---

## Source Tables (Staging Layer)

### stg.customers
| Column | Type | Description |
|---|---|---|
| customer_id | VARCHAR(50) | Unique identifier per order (not per person) |
| customer_unique_id | VARCHAR(50) | Unique customer identity across orders |
| customer_zip_code_prefix | VARCHAR(10) | First 5 digits of ZIP code |
| customer_city | VARCHAR(100) | Customer's city |
| customer_state | VARCHAR(5) | Brazilian state abbreviation (e.g. SP, RJ) |

**Row count:** ~99,441 | **PK:** customer_id (per order)

---

### stg.orders
| Column | Type | Description |
|---|---|---|
| order_id | VARCHAR(50) | Unique order identifier |
| customer_id | VARCHAR(50) | FK → stg.customers |
| order_status | VARCHAR(20) | delivered / shipped / canceled / unavailable / etc. |
| order_purchase_timestamp | DATETIME | When customer placed the order |
| order_approved_at | DATETIME | Payment approval timestamp |
| order_delivered_carrier_date | DATETIME | When handed to logistics carrier |
| order_delivered_customer_date | DATETIME | Actual delivery to customer |
| order_estimated_delivery_date | DATETIME | Estimated delivery promised to customer |

**Row count:** ~99,441 | **PK:** order_id  
**Key derived field:** `delivery_delay_days = delivered_customer_date - estimated_delivery_date`

---

### stg.order_items
| Column | Type | Description |
|---|---|---|
| order_id | VARCHAR(50) | FK → stg.orders |
| order_item_id | INT | Sequential item number within the order |
| product_id | VARCHAR(50) | FK → stg.products |
| seller_id | VARCHAR(50) | FK → stg.sellers |
| shipping_limit_date | DATETIME | Seller's shipping deadline |
| price | DECIMAL(10,2) | Item price in BRL |
| freight_value | DECIMAL(10,2) | Freight cost in BRL |

**Row count:** ~112,650 | **PK:** (order_id, order_item_id) | **Grain of the fact table**

---

### stg.order_payments
| Column | Type | Description |
|---|---|---|
| order_id | VARCHAR(50) | FK → stg.orders |
| payment_sequential | INT | Sequence number (orders can split payment methods) |
| payment_type | VARCHAR(30) | credit_card / boleto / voucher / debit_card |
| payment_installments | INT | Number of installments |
| payment_value | DECIMAL(10,2) | Value of this payment row in BRL |

**Row count:** ~103,886

---

### stg.order_reviews
| Column | Type | Description |
|---|---|---|
| review_id | VARCHAR(50) | Unique review identifier |
| order_id | VARCHAR(50) | FK → stg.orders |
| review_score | TINYINT | Customer rating 1–5 |
| review_comment_title | NVARCHAR(100) | Optional comment title |
| review_comment_message | NVARCHAR(MAX) | Optional free-text review |
| review_creation_date | DATETIME | Survey sent date |
| review_answer_timestamp | DATETIME | When review was submitted |

**Row count:** ~99,224 | **Note:** ~45% of reviews have comment messages

---

### stg.products
| Column | Type | Description |
|---|---|---|
| product_id | VARCHAR(50) | Unique product identifier |
| product_category_name | VARCHAR(100) | Category in Portuguese |
| product_name_lenght | INT | Character count of product name (source typo retained) |
| product_description_lenght | INT | Character count of description |
| product_photos_qty | INT | Number of product photos |
| product_weight_g | INT | Weight in grams |
| product_length_cm | INT | Length in cm |
| product_height_cm | INT | Height in cm |
| product_width_cm | INT | Width in cm |

**Row count:** ~32,951

---

### stg.sellers
| Column | Type | Description |
|---|---|---|
| seller_id | VARCHAR(50) | Unique seller identifier |
| seller_zip_code_prefix | VARCHAR(10) | Seller's ZIP prefix |
| seller_city | VARCHAR(100) | Seller's city |
| seller_state | VARCHAR(5) | Seller's state |

**Row count:** ~3,095

---

### stg.geolocation
| Column | Type | Description |
|---|---|---|
| geolocation_zip_code_prefix | VARCHAR(10) | ZIP prefix |
| geolocation_lat | DECIMAL(9,6) | Latitude |
| geolocation_lng | DECIMAL(9,6) | Longitude |
| geolocation_city | VARCHAR(100) | City name |
| geolocation_state | VARCHAR(5) | State abbreviation |

**Row count:** ~1,000,163 | **Note:** Multiple lat/lng per ZIP — aggregated (AVG) in dim_geography

---

### stg.product_category
| Column | Type | Description |
|---|---|---|
| product_category_name | VARCHAR(100) | Portuguese category name |
| product_category_name_english | VARCHAR(100) | English translation |

**Row count:** ~71

---

### stg.exchange_rates *(API source)*
| Column | Type | Description |
|---|---|---|
| rate_date | DATE | Date of the rate |
| brl_per_usd | DECIMAL(10,6) | How many BRL per 1 USD |
| usd_per_brl | DECIMAL(10,6) | How many USD per 1 BRL |

**Source:** Frankfurter API (https://api.frankfurter.app)  
**Coverage:** All unique order purchase dates in stg.orders

---

## Data Warehouse Layer (Star Schema)

### dw.fact_order_items *(Grain: 1 row per order item)*
| Column | Type | Description |
|---|---|---|
| order_item_key | INT IDENTITY | Surrogate PK |
| order_id | VARCHAR(50) | Degenerate dimension (natural key) |
| order_item_id | INT | Degenerate dimension |
| customer_key | INT | FK → dim_customer |
| product_key | INT | FK → dim_product |
| seller_key | INT | FK → dim_seller |
| date_key | INT | FK → dim_date (YYYYMMDD) |
| geo_key | INT | FK → dim_geography (nullable) |
| price_brl | DECIMAL(10,2) | Item price in BRL |
| price_usd | DECIMAL(10,2) | Item price in USD (via exchange rate) |
| freight_value | DECIMAL(10,2) | Freight cost in BRL |
| review_score | TINYINT | 1–5 customer rating (NULL if no review) |
| delivery_delay_days | INT | Delivered minus estimated (neg = early) |
| order_status | VARCHAR(20) | Degenerate dim |
| payment_type | VARCHAR(30) | Degenerate dim |
| payment_value | DECIMAL(10,2) | Total payment for the order |

---

### dw.dim_customer
| Column | Description |
|---|---|
| customer_key | Surrogate PK |
| customer_id | Natural key |
| city | Title-cased city |
| state | State abbreviation |
| zip_prefix | ZIP prefix |

**SCD Type 1** · **Rows:** ~99,441

---

### dw.dim_product
| Column | Description |
|---|---|
| product_key | Surrogate PK |
| product_id | Natural key |
| category_pt | Portuguese category name |
| category_en | English category name (joined from translation table) |
| weight_g / length_cm / height_cm / width_cm | Physical dimensions |

**SCD Type 1** · **Rows:** ~32,951

---

### dw.dim_seller
| Column | Description |
|---|---|
| seller_key | Surrogate PK |
| seller_id | Natural key |
| city / state / zip_prefix | Location |

**SCD Type 1** · **Rows:** ~3,095

---

### dw.dim_date
| Column | Description |
|---|---|
| date_key | YYYYMMDD integer PK |
| full_date / day / month / month_name / quarter / year | Calendar attributes |
| weekday_num / weekday_name / is_weekend | Day-of-week attributes |

**Populated:** 2016-01-01 → 2019-12-31 (1,461 rows)  
**Hierarchy:** Year → Quarter → Month → Day

---

### dw.dim_geography
| Column | Description |
|---|---|
| geo_key | Surrogate PK |
| zip_prefix | Natural key (unique per row) |
| lat / lng | Averaged coordinates for the ZIP prefix |
| city / state | Location |

**SCD Type 1** · **Rows:** ~19,015 (unique ZIP prefixes)  
**Hierarchy:** State → City

---

## Data Mart Layer

### dw.logistics_performance_mart *(View)*
Pre-aggregated by seller state × customer state × year × month.  
**Target users:** Operations / Logistics team  
**Key measures:** avg_delay_days, late_deliveries, on_time_deliveries, avg_freight_brl, avg_review_score

### dw.sales_performance_mart *(View)*
Pre-aggregated by product category × year × quarter × month.  
**Target users:** Sales / Product management  
**Key measures:** total_revenue_brl, total_revenue_usd, avg_order_value_brl, avg_review_score

---

## Data Quality Notes

| Issue | Resolution |
|---|---|
| `customer_id` is per-order, not per-person | `customer_unique_id` used where person-level granularity needed |
| Product IDs stored as floats by some tools | Loaded as VARCHAR(50) throughout |
| Multiple reviews per order | Deduplicated: keep first review by review_id |
| Geolocation has multiple lat/lng per ZIP | Aggregated: AVG(lat/lng) per zip_prefix |
| Weekend/holiday exchange rates missing | Forward-filled from nearest prior business day |
| Portuguese category names | Joined to translation table; English name used in dim_product |
| ~45% orders have no review | `review_score` nullable in fact table |
| Delivered date NULL for non-delivered orders | `delivery_delay_days` is NULL for those rows |
