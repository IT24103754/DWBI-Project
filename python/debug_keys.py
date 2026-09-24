import sys, pyodbc
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=OlistDW;Trusted_Connection=yes;TrustServerCertificate=yes;')
cur = conn.cursor()

# Check date type
cur.execute('SELECT TOP 1 CONVERT(DATE, order_purchase_timestamp) AS purchase_date FROM stg.orders')
row = cur.fetchone()
d = row[0]
print('date type:', type(d), 'value:', d)
dk = int(d.strftime('%Y%m%d'))
print('date_key:', dk)
cur.execute(f'SELECT COUNT(*) FROM dw.dim_date WHERE date_key = {dk}')
print('dim_date match:', cur.fetchone()[0])

# Check key matches - orders customer_id vs order_items
cur.execute('SELECT TOP 3 oi.order_id, o.customer_id FROM stg.order_items oi JOIN stg.orders o ON oi.order_id=o.order_id')
print('\nSample join:')
for r in cur.fetchall(): print(' ', r)

# Check if customers from orders exist in dim_customer
cur.execute('''
    SELECT COUNT(*) FROM stg.orders o
    JOIN dw.dim_customer dc ON o.customer_id = dc.customer_id
''')
print('\nOrders with matching dim_customer:', cur.fetchone()[0])

# Check if products from order_items exist in dim_product
cur.execute('''
    SELECT COUNT(*) FROM stg.order_items oi
    JOIN dw.dim_product dp ON oi.product_id = dp.product_id
''')
print('Order items with matching dim_product:', cur.fetchone()[0])

conn.close()
