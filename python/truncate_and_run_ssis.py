import pyodbc
import subprocess

conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=Olist_DW;Trusted_Connection=yes;TrustServerCertificate=yes;', autocommit=True)
cur = conn.cursor()

print("Truncating target Fact and Dimension tables in Olist_DW...")
cur.execute("TRUNCATE TABLE dbo.Fact_Orders;")
cur.execute("DELETE FROM dbo.Dim_Customer; DBCC CHECKIDENT ('dbo.Dim_Customer', RESEED, 0);")
cur.execute("DELETE FROM dbo.Dim_Product; DBCC CHECKIDENT ('dbo.Dim_Product', RESEED, 0);")

# Ensure Dim_Seller has the 3,095 sellers
cur.execute("SELECT COUNT(*) FROM dbo.Dim_Seller;")
if cur.fetchone()[0] == 0:
    cur.execute("""
        INSERT INTO dbo.Dim_Seller (SellerBK, SellerZipCode, SellerCity, SellerState)
        SELECT seller_id, seller_zip_code_prefix, seller_city, seller_state FROM Olist_OLTP.dbo.olist_sellers_dataset;
    """)

# Ensure Dim_Date has calendar dates
cur.execute("SELECT COUNT(*) FROM dbo.Dim_Date;")
if cur.fetchone()[0] == 0:
    cur.execute("""
        DECLARE @StartDate DATE = '2016-01-01', @EndDate DATE = '2019-12-31';
        WITH DateRange AS (
            SELECT @StartDate AS [Date]
            UNION ALL
            SELECT DATEADD(day, 1, [Date]) FROM DateRange WHERE [Date] < @EndDate
        )
        INSERT INTO dbo.Dim_Date (DateKey, [Date], [Year], [Quarter], [Month], MonthName, [Day], DayOfWeek, DayName, IsWeekend)
        SELECT 
            CAST(CONVERT(VARCHAR(8), [Date], 112) AS INT),
            [Date], YEAR([Date]), DATEPART(quarter, [Date]), MONTH([Date]), DATENAME(month, [Date]),
            DAY([Date]), DATEPART(weekday, [Date]), DATENAME(weekday, [Date]),
            CASE WHEN DATEPART(weekday, [Date]) IN (1, 7) THEN 1 ELSE 0 END
        FROM DateRange OPTION (MAXRECURSION 3000);
    """)

cur.close()
conn.close()

print("Executing SSIS Package.dtsx via DTExec...")
cmd = [r"C:\Program Files\Microsoft SQL Server\170\DTS\Binn\DTExec.exe", "/File", r"ssis\Olist_ETL\Package.dtsx"]
res = subprocess.run(cmd, capture_output=True, text=True)
print(f"DTExec Exit Code: {res.returncode}")

conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=Olist_DW;Trusted_Connection=yes;TrustServerCertificate=yes;', autocommit=True)
cur = conn.cursor()
print("\n--- Verified Warehouse Counts after Clean SSIS Run ---")
for tbl in ['Dim_Customer', 'Dim_Product', 'Dim_Seller', 'Dim_Date', 'Fact_Orders']:
    cur.execute(f"SELECT COUNT(*) FROM dbo.{tbl}")
    cnt = cur.fetchone()[0]
    print(f"  {tbl:15s} : {cnt:>10,} rows")
cur.close()
conn.close()
