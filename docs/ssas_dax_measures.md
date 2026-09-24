# SSAS Tabular Model – DAX Measures & Configuration Guide

> IT3101 DWBI Project · Olist Brazilian E-Commerce  
> Build in: **SQL Server Data Tools (SSDT)** → Analysis Services Tabular Project  
> Mode: **In-Memory (Tabular)** | Compatibility: 1600+

---

## 1. Model Setup in SSDT

1. **File → New → Project → Analysis Services Tabular Project**
2. Server: `localhost` (your local SSAS Tabular instance)
3. Compatibility Level: `SQL Server 2019 / 2025 (1600)`

### Import Tables (from OlistDW)
Connect to: `Data Source = localhost; Initial Catalog = OlistDW`

Import these tables:
- `dw.fact_order_items`
- `dw.dim_customer`
- `dw.dim_product`
- `dw.dim_seller`
- `dw.dim_date`
- `dw.dim_geography`

---

## 2. Relationships (Diagram View)

| From (Many) | To (One) | Key |
|---|---|---|
| fact_order_items | dim_customer | customer_key |
| fact_order_items | dim_product | product_key |
| fact_order_items | dim_seller | seller_key |
| fact_order_items | dim_date | date_key |
| fact_order_items | dim_geography | geo_key |

> All relationships are **Many-to-One**, **Single** direction filter.

---

## 3. Hierarchies

### dim_date → [Date Hierarchy]
```
Year → Quarter → Month → Day
(columns: year, quarter, month_name, full_date)
```

### dim_geography → [Location Hierarchy]
```
State → City
(columns: state, city)
```

### dim_product → [Category Hierarchy]
```
Category (category_en)
```

---

## 4. DAX Measures

Add all measures to `fact_order_items` table.

### Revenue Measures

```dax
Total Revenue BRL :=
    SUM ( fact_order_items[price_brl] )

Total Revenue USD :=
    SUM ( fact_order_items[price_usd] )

Total Freight BRL :=
    SUM ( fact_order_items[freight_value] )

Avg Order Value BRL :=
    AVERAGEX (
        VALUES ( fact_order_items[order_id] ),
        CALCULATE ( SUM ( fact_order_items[price_brl] ) )
    )
```

### Order & Volume Measures

```dax
Order Count :=
    DISTINCTCOUNT ( fact_order_items[order_id] )

Order Item Count :=
    COUNTROWS ( fact_order_items )
```

### Delivery Measures

```dax
Avg Delivery Delay Days :=
    AVERAGE ( fact_order_items[delivery_delay_days] )

Late Delivery Count :=
    CALCULATE (
        COUNTROWS ( fact_order_items ),
        fact_order_items[delivery_delay_days] > 0
    )

On Time Delivery Count :=
    CALCULATE (
        COUNTROWS ( fact_order_items ),
        fact_order_items[delivery_delay_days] <= 0
    )

Late Delivery % :=
    DIVIDE (
        [Late Delivery Count],
        [Order Item Count],
        0
    ) * 100
```

### Satisfaction Measures

```dax
Avg Review Score :=
    AVERAGE ( fact_order_items[review_score] )

5-Star Count :=
    CALCULATE (
        COUNTROWS ( fact_order_items ),
        fact_order_items[review_score] = 5
    )

1-Star Count :=
    CALCULATE (
        COUNTROWS ( fact_order_items ),
        fact_order_items[review_score] = 1
    )
```

### Freight Analysis

```dax
Avg Freight BRL :=
    AVERAGE ( fact_order_items[freight_value] )

Freight as % of Revenue :=
    DIVIDE (
        [Total Freight BRL],
        [Total Revenue BRL],
        0
    ) * 100
```

### Time Intelligence

```dax
Revenue MoM % Change :=
    VAR CurrentRevenue = [Total Revenue BRL]
    VAR PriorRevenue =
        CALCULATE (
            [Total Revenue BRL],
            PREVIOUSMONTH ( dim_date[full_date] )
        )
    RETURN
        DIVIDE ( CurrentRevenue - PriorRevenue, PriorRevenue, BLANK() ) * 100

YTD Revenue BRL :=
    CALCULATE (
        [Total Revenue BRL],
        DATESYTD ( dim_date[full_date] )
    )
```

---

## 5. KPIs

In the Tabular Model Editor, create KPIs for:

| Base Measure | Target | Status Threshold |
|---|---|---|
| Avg Review Score | 4.5 | Red < 3.5, Yellow < 4.5, Green ≥ 4.5 |
| Avg Delivery Delay Days | 0 | Red > 7, Yellow > 0, Green ≤ 0 |
| Late Delivery % | 10% | Red > 30%, Yellow > 10%, Green ≤ 10% |

---

## 6. Deploy the Model

1. In SSDT: **Build → Deploy** (deploying to `localhost`)
2. Model name: `OlistTabularModel`
3. Verify in **SQL Server Management Studio → Analysis Services → Databases → OlistTabularModel**

---

## 7. Connect Power BI

1. Open **Power BI Desktop**
2. **Get Data → Analysis Services**
3. Server: `localhost`
4. Database: `OlistTabularModel`
5. Select **Connect live** (do NOT import — keeps it true OLAP)
6. Select the `Model` table set

---

## 8. Power BI Dashboard Pages

### Page 1 – Executive Summary
- **KPI Cards:** Total Revenue BRL, Order Count, Avg Review Score, Avg Delivery Delay Days, Late Delivery %
- **Trend Line:** Monthly Revenue BRL (dim_date[Year/Month] vs [Total Revenue BRL])
- **Gauge:** Avg Review Score vs 4.5 target

### Page 2 – Trend & Category Analysis
- **Line Chart:** Monthly Revenue BRL + Late Delivery % (dual axis) by Year/Month
- **Bar Chart:** Top 15 Product Categories by Revenue BRL
- **Scatter:** Avg Delay Days vs Avg Review Score (by category)
- **Slicers:** Year, Quarter

### Page 3 – Geographic & Interactive Analysis
- **Map Visual:** dim_geography[lat/lng], bubble size = Order Item Count
- **Bar Chart:** Revenue by seller state
- **Bar Chart:** Avg Review Score by customer state
- **Matrix:** seller state × year → Avg Delivery Delay Days
- **Slicers:** State (customer), Category, Year, Review Score

---

## 9. Formatting Tips

- Set `price_brl`, `price_usd`, `freight_value` to **Currency, 2 decimal places**
- Set `delivery_delay_days` to **Whole number**
- Set `review_score` to **Decimal, 1 place**
- Hide surrogate key columns from Report View
- Hide natural key columns from Report View (keep in model for debugging)
