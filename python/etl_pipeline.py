"""
IT3101 DWBI Project – Olist Brazilian E-Commerce
Python ETL Pipeline – Full end-to-end execution
Run: python etl_pipeline.py

Steps:
  1. Creates DB / staging / star schema (runs SQL scripts)
  2. Loads all 9 CSVs into stg.* tables
  3. Fetches exchange rates from Frankfurter API
  4. Transforms and loads dimension tables
  5. Transforms and loads fact_order_items
  6. Creates data mart views
  7. Runs validation tests
"""

import os
import sys
import subprocess

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'sql')
PYTHON_DIR  = os.path.dirname(__file__)

def run_script(name):
    path = os.path.join(PYTHON_DIR, name)
    print(f"\n{'='*60}")
    print(f"  Running: {name}")
    print(f"{'='*60}")
    result = subprocess.run([sys.executable, path], capture_output=False)
    if result.returncode != 0:
        print(f"[ERROR] {name} failed with code {result.returncode}")
        sys.exit(result.returncode)

def run_sql(filename):
    """Execute a SQL script via sqlcmd."""
    sql_path = os.path.join(SCRIPTS_DIR, filename)
    print(f"\n{'='*60}")
    print(f"  SQL Script: {filename}")
    print(f"{'='*60}")
    result = subprocess.run(
        ['sqlcmd', '-S', 'localhost', '-C', '-i', sql_path],
        capture_output=False
    )
    if result.returncode != 0:
        print(f"[ERROR] SQL script {filename} failed.")
        sys.exit(result.returncode)

if __name__ == '__main__':
    print("="*60)
    print("  OLIST DWBI – Full ETL Pipeline")
    print("="*60)

    # Step 1: Create schemas
    run_sql('01_staging_schema.sql')
    run_sql('02_star_schema.sql')

    # Step 2: Load CSVs into staging
    run_script('01_load_staging.py')

    # Step 3: Fetch exchange rates
    run_script('02b_exchange_rates_seed.py')

    # Step 4 & 5: Load dimensions + fact
    run_script('03_load_dimensions.py')
    run_script('04_load_fact.py')

    # Step 6: Data mart
    run_sql('03_data_mart.sql')

    # Step 7: Validation
    run_sql('04_validation_tests.sql')

    print("\n" + "="*60)
    print("  ETL PIPELINE COMPLETE!")
    print("="*60)
