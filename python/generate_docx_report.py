"""
IT3101 DWBI Project - Generate Academic Word Document (.docx)
Builds a beautifully styled Microsoft Word submission document
matching all 8 tasks and the assignment marking rubric.
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

DOCS_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')
TARGET_DOCX = os.path.join(DOCS_DIR, 'IT3101_DWBI_Assignment_Submission_Report.docx')

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def add_callout(doc, text, title="NOTE"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F0F4F8")
    set_cell_margins(cell, top=120, bottom=120, left=200, right=200)
    
    # Left border highlight
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="005691"/>
            <w:top w:val="none"/>
            <w:right w:val="none"/>
            <w:bottom w:val="none"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    r_title = p.add_run(f"[{title}] ")
    r_title.bold = True
    r_title.font.color.rgb = RGBColor(0x00, 0x56, 0x91)
    r_text = p.add_run(text)
    r_text.font.size = Pt(10)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def style_table(tbl, header_bg="005691", alt_bg="F9FBFC"):
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(tbl.rows):
        for cell in row.cells:
            set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
            if i == 0:
                set_cell_background(cell, header_bg)
                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(2)
                    p.paragraph_format.space_after = Pt(2)
                    for r in p.runs:
                        r.bold = True
                        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                        r.font.size = Pt(9.5)
            else:
                if i % 2 == 1:
                    set_cell_background(cell, "FFFFFF")
                else:
                    set_cell_background(cell, alt_bg)
                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(2)
                    p.paragraph_format.space_after = Pt(2)
                    for r in p.runs:
                        r.font.size = Pt(9)

def main():
    print("Generating Academic Word Report...")
    doc = Document()

    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    # ── COVER / TITLE ──────────────────────────────────────────
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(36)
    p_title.paragraph_format.space_after = Pt(6)
    r_main = p_title.add_run("IT3101 – Data Warehousing & Business Intelligence")
    r_main.bold = True
    r_main.font.size = Pt(22)
    r_main.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(24)
    r_sub = p_sub.add_run("Design and Implementation of an End-to-End Data Warehouse and Business Intelligence Solution\nCase Study: Brazilian E-Commerce Marketplace (Olist)")
    r_sub.font.size = Pt(14)
    r_sub.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    # Metadata Box
    meta_tbl = doc.add_table(rows=6, cols=2)
    meta_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Module Code & Title:", "IT3101 - Data Warehousing & Business Intelligence"),
        ("Academic Level:", "BSc (Hons) in Information Technology / Computing"),
        ("Assignment Title:", "Design and Implementation of a DWBI Solution"),
        ("Business Scenario:", "Olist Brazilian E-Commerce Marketplace (2016–2018)"),
        ("Technology Stack:", "SQL Server 2025, SSIS / Python ETL, SSAS Tabular, Power BI"),
        ("Submission Type:", "Comprehensive Technical Report & Practical Artifacts")
    ]
    for idx, (k, v) in enumerate(meta_data):
        row = meta_tbl.rows[idx]
        row.cells[0].paragraphs[0].add_run(k).bold = True
        row.cells[1].paragraphs[0].add_run(v)
    style_table(meta_tbl, header_bg="003366")
    doc.add_page_break()

    # ── EXECUTIVE SUMMARY ──────────────────────────────────────
    h1 = doc.add_heading("Executive Summary", level=1)
    h1.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    
    p = doc.add_paragraph(
        "Modern multi-sided marketplace platforms face operational and strategic challenges in balancing buyer "
        "satisfaction, seller logistics performance, and geographic expansion. This report presents a production-grade, "
        "end-to-end Data Warehouse and Business Intelligence (DW/BI) solution engineered on the real-world operational dataset "
        "of Olist, Brazil's premier e-commerce marketplace platform, encompassing 99,441 customer orders and 112,650 order items "
        "from 2016 through 2018."
    )
    p = doc.add_paragraph(
        "The project integrates three heterogeneous data source types (9 operational CSV flat files, a normalized SQL Server relational "
        "database staging layer, and an external macroeconomic exchange-rate REST API). The dimensional storage layer implements a "
        "Kimball-standard Star Schema anchored on dw.fact_order_items and surrounded by five conformed dimensions (Customer, Product, "
        "Seller, Date, Geography). Zero orphan foreign keys exist across all 112,650 fact rows. Two specialized data marts "
        "(Logistics Performance and Sales Performance) provide targeted aggregation layers. An SSAS Tabular semantic model with 17 custom "
        "DAX measures powers an interactive 3-page Power BI dashboard. Finally, five empirical business hypotheses were validated through "
        "direct analytical queries to provide actionable strategic recommendations."
    )

    # ── CLEAR AI USAGE DECLARATION ─────────────────────────────
    h1 = doc.add_heading("Declaration of AI Usage (CLEAR Framework)", level=1)
    h1.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    ai_tbl = doc.add_table(rows=6, cols=2)
    ai_data = [
        ("Framework Pillar", "Application and Academic Governance"),
        ("Context (C)", "AI was utilized for boilerplate DDL script generation, formatting XML/BIM and DAX measure syntaxes, and accelerating repetitive tabular declarations."),
        ("Limitations (L)", "AI tools lacked local database environment connectivity, requiring human intervention for SQL Server ODBC driver configuration, data type resolution (Decimal vs NumPy), and syntax fixes."),
        ("Evaluation (E)", "All generated queries, schemas, and ETL pipelines were independently tested against raw Kaggle source files and verified through automated validation scripts."),
        ("Adaptation (A)", "The ETL design was adapted into a hybrid Python/SSIS architecture to ensure automated reproducibility and continuous validation while maintaining full SSIS package compliance."),
        ("Responsibility (R)", "The final dimensional architecture, grain determination, surrogate key strategy, and strategic business recommendations represent the verified intellectual work of the student.")
    ]
    for idx, (c1, c2) in enumerate(ai_data):
        ai_tbl.rows[idx].cells[0].paragraphs[0].add_run(c1)
        ai_tbl.rows[idx].cells[1].paragraphs[0].add_run(c2)
    style_table(ai_tbl, header_bg="2C3E50")

    doc.add_page_break()

    # ── TASK 1: DATASET & BUSINESS SCENARIO ────────────────────
    h1 = doc.add_heading("Task 1: Dataset Selection and Business Scenario Identification", level=1)
    h1.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    doc.add_heading("1.1 Business Domain & Operational Environment", level=2)
    doc.add_paragraph(
        "The selected business domain is Retail / Multi-Sided E-Commerce. Olist functions as a marketplace integrator connecting small, "
        "independent merchant businesses throughout Brazil with major e-commerce storefronts (Mercado Livre, B2W, Amazon Brazil). "
        "Olist manages catalog listing, order fulfillment coordination via national logistics carrier agreements, and customer review collection."
    )

    doc.add_heading("1.2 Purpose of the Analytical System", level=2)
    doc.add_paragraph(
        "While Olist's operational OLTP databases excel at recording daily checkout transactions, they cannot effectively evaluate cross-state "
        "freight cost burdens, identify merchants causing delivery bottlenecks, or decouple physical merchandise quality issues from shipping delays. "
        "This DW/BI solution establishes a centralized single source of truth for cross-functional performance analytics."
    )

    doc.add_heading("1.3 Dataset Statistics & Profile", level=2)
    ds_tbl = doc.add_table(rows=10, cols=4)
    ds_data = [
        ("Operational Source File", "Source Entity", "Record Count", "Key Attributes"),
        ("olist_orders_dataset.csv", "Orders", "99,441", "order_id, customer_id, order_status, purchase/delivered timestamps"),
        ("olist_order_items_dataset.csv", "Order Items", "112,650", "order_id, order_item_id, product_id, seller_id, price, freight_value"),
        ("olist_customers_dataset.csv", "Customers", "99,441", "customer_id, customer_unique_id, zip_code, city, state"),
        ("olist_products_dataset.csv", "Products", "32,951", "product_id, category_name, weight_g, length_cm, height_cm, width_cm"),
        ("olist_sellers_dataset.csv", "Sellers", "3,095", "seller_id, zip_code, city, state"),
        ("olist_order_payments_dataset.csv", "Payments", "103,886", "order_id, payment_sequential, payment_type, installments, payment_value"),
        ("olist_order_reviews_dataset.csv", "Reviews", "99,224", "review_id, order_id, review_score (1-5), review_comment_message"),
        ("olist_geolocation_dataset.csv", "Coordinates", "1,000,163", "zip_prefix, lat, lng, city, state"),
        ("product_category_name_translation.csv", "Taxonomy", "71", "product_category_name (Portuguese & English)")
    ]
    for idx, row in enumerate(ds_data):
        for col_idx, text in enumerate(row):
            ds_tbl.rows[idx].cells[col_idx].paragraphs[0].add_run(text)
    style_table(ds_tbl)

    doc.add_heading("1.4 Suitability for Dimensional Modeling", level=2)
    doc.add_paragraph(
        "1. OLTP Architecture: Real-world 3NF data capturing orders, line items, reviews, and installments.\n"
        "2. High Granularity: 112,650 line-item rows provide genuine analytical volume for drill-down and slicing.\n"
        "3. Natural Dimensional Conformation: Naturally relates to temporal, geographic, merchant, and product entities.\n"
        "4. Real-world Data Quality Challenges: Includes multi-point coordinates, untranslated terms, and variable freight charges."
    )

    # ── TASK 2: DATA SOURCE PREPARATION ────────────────────────
    h1 = doc.add_heading("Task 2: Data Source Identification and Preparation", level=1)
    h1.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    doc.add_heading("2.1 Multi-Source Integration (3 Heterogeneous Types)", level=2)
    doc.add_paragraph(
        "To satisfy Task 2's requirement for multiple source types, three distinct input mechanisms were unified into the staging area:\n"
        "• Source Type 1 (Flat Files): 9 CSV operational extracts provided as delimited UTF-8 files.\n"
        "• Source Type 2 (Relational DB): Loaded into SQL Server relational staging tables (stg.*) with PK/FK indexes representing the operational transactional store.\n"
        "• Source Type 3 (External Web REST API): Frankfurter Currency API (https://api.frankfurter.app) queried for daily BRL->USD conversion rates across all 634 unique order dates."
    )

    doc.add_heading("2.2 Data Cleansing and Preparation Procedures", level=2)
    doc.add_paragraph(
        "• String Normalization: Casing discrepancies and trailing whitespace in city and category attributes were standardized using Title Case.\n"
        "• Category Bilingual Join: Portuguese taxonomy was joined with English translation tables to generate readable category hierarchies.\n"
        "• Geolocation Centroid Averaging: Over 1 million GPS coordinate rows were condensed into 19,015 unique zip code centroids using arithmetic mean aggregation (AVG(lat), AVG(lng)).\n"
        "• Review Deduplication: Window ranking partitioned by order_id retained only the primary customer rating per order.\n"
        "• Exchange Rate Calendar Alignment: Weekend and holiday currency rate gaps were forward-filled from the prior active business day."
    )

    # ── TASK 3: ARCHITECTURE DESIGN ───────────────────────────
    h1 = doc.add_heading("Task 3: Data Warehouse Architecture Design", level=1)
    h1.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    doc.add_paragraph(
        "The architecture implements a standard 5-layer enterprise data warehousing framework based on Kimball dimensional methodologies:"
    )
    add_callout(doc, "The full visual architecture diagram and star schema diagram are available in docs/architecture_diagram.drawio and can be opened in the installed draw.io application.", "ARCHITECTURAL DIAGRAM")

    arch_tbl = doc.add_table(rows=6, cols=3)
    arch_data = [
        ("Layer", "Components & Technologies", "Functional Role"),
        ("1. Source Layer", "9 CSV flat files, SQL Server OLTP mirror, Frankfurter REST API", "Captures raw operational business transactions and external currency data."),
        ("2. Integration Layer", "Python pyodbc fast_executemany / SSIS PKG_01-PKG_03, dw.etl_run_log", "Extracts, transforms, standardizes, enriches, and reconciles incoming feeds."),
        ("3. Storage Layer", "SQL Server 2025 (stg.* staging schema, dw.* Star Schema, data mart views)", "Persistent, ACID-compliant enterprise storage with surrogate keys and referential integrity."),
        ("4. Semantic / OLAP Layer", "SSAS Tabular Model (Compatibility Level 1600), 17 DAX measures, hierarchies", "In-memory VertiPaq engine providing rapid DAX measure computation and dimensional navigation."),
        ("5. Presentation Layer", "Power BI Desktop (DirectQuery & Import pbids), 3 analytical dashboard pages", "Executive dashboards, trend lines, category rankings, and interactive geographic drill-down.")
    ]
    for idx, row in enumerate(arch_data):
        for col_idx, text in enumerate(row):
            arch_tbl.rows[idx].cells[col_idx].paragraphs[0].add_run(text)
    style_table(arch_tbl)

    doc.add_page_break()

    # ── TASK 4: DIMENSIONAL MODELING ───────────────────────────
    h1 = doc.add_heading("Task 4: Dimensional Data Warehouse Design and Implementation", level=1)
    h1.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    doc.add_heading("4.1 Grain and Fact Table Architecture", level=2)
    doc.add_paragraph(
        "• Business Process: Marketplace item ordering and shipment fulfillment.\n"
        "• Grain: One row per order line item (order_id + order_item_id).\n"
        "• Surrogate Key: order_item_key (INT IDENTITY(1,1) PRIMARY KEY).\n"
        "• Additive Measures: price_brl, price_usd, freight_value, payment_value.\n"
        "• Semi-Additive / Ordinal Measures: review_score (1-5), delivery_delay_days (transit variance).\n"
        "• Degenerate Dimensions: order_id, order_item_id, order_status, payment_type."
    )

    doc.add_heading("4.2 Conformed Dimension Tables", level=2)
    dim_tbl = doc.add_table(rows=6, cols=4)
    dim_data = [
        ("Dimension Table", "Surrogate PK", "Row Count", "Hierarchies / Core Attributes"),
        ("dw.dim_customer", "customer_key", "99,441", "customer_id (NK), city, state, zip_prefix"),
        ("dw.dim_product", "product_key", "32,951", "product_id (NK), category_en, category_pt, weight_g, dimensions"),
        ("dw.dim_seller", "seller_key", "3,095", "seller_id (NK), city, state, zip_prefix"),
        ("dw.dim_date", "date_key", "1,461", "Hierarchy: Year > Quarter > Month > Day (2016-2019)"),
        ("dw.dim_geography", "geo_key", "19,015", "Hierarchy: State > City (zip_prefix NK, lat, lng centroids)")
    ]
    for idx, row in enumerate(dim_data):
        for col_idx, text in enumerate(row):
            dim_tbl.rows[idx].cells[col_idx].paragraphs[0].add_run(text)
    style_table(dim_tbl)

    doc.add_heading("4.3 Slowly Changing Dimension (SCD) Policy", level=2)
    doc.add_paragraph(
        "All dimensions implement SCD Type 1 (Overwrite). This strategy is academically justified because the Olist dataset represents "
        "a closed historical corpus (2016–2018). Tracking address mutations or seller migrations via surrogate versioning (Type 2) would artificially "
        "inflate dimension volume without providing authentic historical validity for completed historical deliveries."
    )

    # ── TASK 5: ETL PROCESS DEVELOPMENT ───────────────────────
    h1 = doc.add_heading("Task 5: ETL Process Development", level=1)
    h1.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    doc.add_heading("5.1 Workflow Structure & Load Sequence", level=2)
    doc.add_paragraph(
        "The ETL pipeline is orchestrated via python/etl_pipeline.py and mirrored in SSIS packages (PKG_01 through PKG_03):\n"
        "1. Schema Build: Executes 01_staging_schema.sql and 02_star_schema.sql.\n"
        "2. Staging Extract: Chunked ingestion of 9 raw CSVs into stg.* tables (1,550,922 rows total).\n"
        "3. Financial Seed: 02b_exchange_rates_seed.py enriches stg.exchange_rates for all 634 dates.\n"
        "4. Dimension Transform: 03_load_dimensions.py clears and loads customer, product, seller, and geography dimensions.\n"
        "5. Fact Integration: 04_load_fact.py performs SQL key resolution and loads 112,650 rows into dw.fact_order_items.\n"
        "6. Data Mart Deployment: 03_data_mart.sql compiles analytical views.\n"
        "7. Verification: 04_validation_tests.sql executes automated row reconciliation."
    )

    doc.add_heading("5.2 Validation & Integrity Results", level=2)
    val_tbl = doc.add_table(rows=7, cols=4)
    val_data = [
        ("Test Category", "Metric Tested", "Actual Result", "Status"),
        ("Source Staging Volume", "Total rows in stg.* tables", "1,550,922 rows", "PASSED (100% Reconciliation)"),
        ("Fact Granularity", "Total rows in dw.fact_order_items", "112,650 rows", "PASSED (Matches Source Items)"),
        ("Distinct Order Count", "Unique orders in fact table", "98,666 orders", "PASSED"),
        ("Referential Integrity", "Orphan Customer, Product, Seller, Date keys", "0 orphans (Zero defects)", "PASSED (100% Integrity)"),
        ("Financial Validation", "Cumulative BRL gross revenue", "R$ 13,591,643.70", "PASSED"),
        ("Lead-Time Variance", "Average delivery delay days", "-12.03 days (early)", "PASSED")
    ]
    for idx, row in enumerate(val_data):
        for col_idx, text in enumerate(row):
            val_tbl.rows[idx].cells[col_idx].paragraphs[0].add_run(text)
    style_table(val_tbl)

    # ── TASK 6: DATA MART DEVELOPMENT ─────────────────────────
    h1 = doc.add_heading("Task 6: Data Mart Development", level=1)
    h1.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    doc.add_paragraph(
        "To optimize query throughput for specific operational divisions, two departmental data marts were constructed as pre-aggregated SQL views:"
    )
    doc.add_heading("6.1 dw.logistics_performance_mart", level=2)
    doc.add_paragraph(
        "• Target Users: Chief Logistics Officer, Carrier Relationship Managers, Interstate Dispatchers.\n"
        "• Aggregation Grain: Seller State × Customer State × Year × Month.\n"
        "• Measures: avg_delay_days, max_delay_days, late_deliveries, on_time_deliveries, avg_freight_brl, total_freight_brl, avg_review_score.\n"
        "• Analytical Benefit: Rapidly isolates problematic interstate transport corridors without scanning the full 112K item fact table."
    )

    doc.add_heading("6.2 dw.sales_performance_mart", level=2)
    doc.add_paragraph(
        "• Target Users: Merchandising Directors, Category Brand Managers, Commercial Executives.\n"
        "• Aggregation Grain: Product Category × Year × Quarter × Month.\n"
        "• Measures: order_item_count, distinct_order_count, total_revenue_brl, total_revenue_usd, avg_order_value_brl, avg_review_score."
    )

    # ── TASK 7: OLAP & BI DASHBOARDS ──────────────────────────
    h1 = doc.add_heading("Task 7: OLAP Analysis and Business Intelligence Dashboard Development", level=1)
    h1.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    doc.add_heading("7.1 Semantic Model & DAX Formulas", level=2)
    dax_tbl = doc.add_table(rows=7, cols=3)
    dax_data = [
        ("Measure Name", "DAX Expression", "Business Intent"),
        ("Total Revenue BRL", "SUM(fact_order_items[price_brl])", "Gross marketplace merchandise volume in local currency."),
        ("Total Revenue USD", "SUM(fact_order_items[price_usd])", "Gross merchandise volume normalized in USD."),
        ("Order Count", "DISTINCTCOUNT(fact_order_items[order_id])", "Volume of discrete completed transactions."),
        ("Avg Order Value (AOV)", "AVERAGEX(VALUES(fact_order_items[order_id]), CALCULATE(SUM(fact_order_items[price_brl])))", "Mean basket spend per order."),
        ("Late Delivery %", "DIVIDE(CALCULATE(COUNTROWS(fact_order_items), fact_order_items[delivery_delay_days] > 0), [Order Item Count], 0) * 100", "Proportion of shipments missing promised SLA."),
        ("Avg Review Score", "AVERAGE(fact_order_items[review_score])", "Overall customer satisfaction index (1.00-5.00).")
    ]
    for idx, row in enumerate(dax_data):
        for col_idx, text in enumerate(row):
            dax_tbl.rows[idx].cells[col_idx].paragraphs[0].add_run(text)
    style_table(dax_tbl)

    doc.add_heading("7.2 Power BI Dashboard Specification (3 Pages)", level=2)
    doc.add_paragraph(
        "• Page 1: Executive Summary – KPI cards (Total Revenue R$ 13.59M, 98.6K Orders, 4.03 Review Score, 6.58% Late Rate), monthly GMV trend sparkline, and review score distribution gauge.\n"
        "• Page 2: Trend Analysis – Dual-axis monthly revenue vs late delivery percentage line chart, top 15 category horizontal bar chart, and delay vs review correlation scatter plot.\n"
        "• Page 3: Interactive Geographic Analysis – Spatial bubble map plotting coordinates with volume-weighted radii, state-level freight ratio bar charts, and multi-level drill-down matrices."
    )
    add_callout(doc, "Power BI can be launched immediately by double-clicking powerbi/OlistDW_DirectQuery.pbids or powerbi/OlistDW_Import.pbids.", "POWER BI CONNECTION")

    doc.add_page_break()

    # ── TASK 8: INSIGHTS & RECOMMENDATIONS ────────────────────
    h1 = doc.add_heading("Task 8: Business Insights and Strategic Recommendations", level=1)
    h1.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    doc.add_heading("Insight 1: Shipping Delay is the Single Largest Predictor of Rating Collapse", level=2)
    doc.add_paragraph(
        "• Empirical Evidence (docs/h1_delay_vs_review.csv): Deliveries arriving >7 days early score an average of 4.27/5.00 (83,506 items). "
        "On-time deliveries maintain 4.08/5.00. However, when an order is 1–7 days late, the average review score drops to 2.24/5.00. "
        "For orders >7 days late, ratings collapse to 1.62/5.00.\n"
        "• Recommendation: Implement automated carrier warning alerts when transit exceeds 75% of the estimated window. Trigger automated apology credits prior to review survey issuance."
    )

    doc.add_heading("Insight 2: Severe Regional Freight Inequity in Peripheral Northern States", level=2)
    doc.add_paragraph(
        "• Empirical Evidence (docs/h2_freight_by_state.csv): In São Paulo (SP), freight averages R$ 15.15 (13.5% of item price). "
        "In peripheral states, freight cost ratios are crippling: Paraíba (PB) averages R$ 42.71 (35.7% of price), Roraima (RR) R$ 42.98 (36.5%), and Maranhão (MA) R$ 38.26 (32.4%).\n"
        "• Recommendation: Partner with regional 3PL carriers to establish micro-fulfillment cross-dock hubs in Recife and Salvador, subsidizing peripheral line-haul legs."
    )

    doc.add_heading("Insight 3: Q4 Black Friday Seasonality Generates 146% Revenue Surges", level=2)
    doc.add_paragraph(
        "• Empirical Evidence (docs/h3_monthly_revenue.csv): Monthly revenue in early 2017 averaged R$ 120,000–R$ 400,000. In November 2017 (Black Friday), "
        "gross revenue surged to R$ 1,010,271.37 across 7,289 orders (a 146% jump over October).\n"
        "• Recommendation: Enforce mandatory carrier capacity lock-ins and merchant inventory buffer minimums 60 days prior to Q4."
    )

    doc.add_heading("Insight 4: 80/20 Concentration of Late Deliveries in Chronic Repeat Sellers", level=2)
    doc.add_paragraph(
        "• Empirical Evidence (docs/h4_late_sellers.csv): Out of 3,095 active merchants, the top 20 delinquent sellers account for a massive share of late shipments. "
        "Seller 4a3ca9315b744ce9f4e93744c0c5ae81 accumulated 379 late deliveries (20.9% failure rate), while 1f50f39ac98c342f6d057da81330c985 recorded 225 late orders.\n"
        "• Recommendation: Establish a Seller Performance Tiering policy. Merchants exceeding a 10% late shipping threshold should face algorithmic catalog demotion."
    )

    doc.add_heading("Insight 5: Category Defect Rates Suppress Ratings Independent of Logistics", level=2)
    doc.add_paragraph(
        "• Empirical Evidence (docs/h5_category_reviews.csv): Office Furniture generated an average review score of only 3.49/5.00 across 1,677 orders despite arriving an average "
        "of 11.86 days early. Male Fashion Clothing scored 3.64/5.00 despite arriving 12.86 days early. Conversely, Books General Interest scored 4.45/5.00 under identical shipping times.\n"
        "• Recommendation: Enforce mandatory dimension assembly diagrams and video manuals on furniture listings, and standardized size charts on apparel."
    )

    doc.add_heading("8.1 Strategic Roadmap Matrix", level=2)
    act_tbl = doc.add_table(rows=5, cols=4)
    act_data = [
        ("Timeframe", "Initiative", "Target Objective", "Owner"),
        ("Immediate (30 Days)", "Throttle catalog exposure for top 20 chronic late sellers", "Lower marketplace late rate < 5%", "VP Merchant Operations"),
        ("Short-Term (90 Days)", "Deploy automated proactive pre-delay SMS alerts & vouchers", "Lift late delivery review scores > 3.00", "Head of Customer Experience"),
        ("Medium-Term (180 Days)", "Require assembly video manuals for Office Furniture sellers", "Elevate furniture review score > 4.00", "Category Merchandising Lead"),
        ("Long-Term (365 Days)", "Construct Northeast regional fulfillment consolidation hubs", "Reduce peripheral freight ratio < 20%", "Chief Logistics Officer")
    ]
    for idx, row in enumerate(act_data):
        for col_idx, text in enumerate(row):
            act_tbl.rows[idx].cells[col_idx].paragraphs[0].add_run(text)
    style_table(act_tbl)

    # Save
    doc.save(TARGET_DOCX)
    print(f"Report generated successfully: {TARGET_DOCX}")

if __name__ == '__main__':
    main()
