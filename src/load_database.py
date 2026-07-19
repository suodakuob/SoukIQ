import psycopg2
from psycopg2 import sql
import pandas as pd
from pathlib import Path
import os

# Database Connection Parameters (Standard local Postgres defaults)
DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "postgres"
DB_PASS = "root"  # ⚠️ بدّل هادي للباسورد ديال الـ Postgres ديالك إذا كان مختلف
DB_NAME = "soukiq_db"

BASE_DIR = Path(__file__).resolve().parent.parent
CLEANED_DIR = BASE_DIR / "data" / "cleaned"
SQL_SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"

print("🔌 Connecting to PostgreSQL Server...")

def create_database():
    # Connect to default postgres database first to create the target database
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database="postgres"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Check if target database exists
    cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_NAME,))
    exists = cursor.fetchone()
    
    if not exists:
        print(f"🛠️ Target database '{DB_NAME}' not found. Creating database...")
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
    else:
        print(f"✅ Database '{DB_NAME}' already exists.")
        
    cursor.close()
    conn.close()

def apply_schema():
    print(f"📖 Reading schema definitions from {SQL_SCHEMA_PATH.name}...")
    with open(SQL_SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()
        
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )
    cursor = conn.cursor()
    cursor.execute(schema_sql)
    conn.commit()
    print("✅ SQL Schema and performance indexes successfully applied.")
    cursor.close()
    conn.close()

def load_table_fast(table_name, csv_filename, conn, cursor):
    print(f"⚡ Streaming {csv_filename} data directly to table '{table_name}'...")
    csv_path = CLEANED_DIR / csv_filename
    
    # Handle the transactions Nulls mapping elegantly (converting -1 back to NULL for database sanity)
    if table_name == "fact_transaction":
        df = pd.read_csv(csv_path)
        # Convert -1 placeholder back to empty string so COPY reads it as NULL
        df['campaign_id'] = df['campaign_id'].replace(-1, '')
        temp_csv_path = CLEANED_DIR / "temp_transactions.csv"
        df.to_csv(temp_csv_path, index=False, header=False)
        
        with open(temp_csv_path, 'r', encoding='utf-8') as f:
            cursor.copy_from(f, table_name, sep=',', null='')
        os.remove(temp_csv_path) # Clean up temp file
    else:
        # For merchants, campaigns, outages, load using psycopg2 copy_from
        with open(csv_path, 'r', encoding='utf-8') as f:
            next(f) # Skip CSV header
            cursor.copy_from(f, table_name, sep=',')

def load_all_data():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )
    cursor = conn.cursor()
    
    # Ingestion order matters due to Foreign Keys!
    load_table_fast("dim_merchant", "merchants.csv", conn, cursor)
    load_table_fast("dim_campaign", "campaigns.csv", conn, cursor)
    load_table_fast("dim_outage", "outages.csv", conn, cursor)
    load_table_fast("fact_transaction", "transactions.csv", conn, cursor)
    
    conn.commit()
    
    # Post-load verification count
    cursor.execute("SELECT COUNT(*) FROM fact_transaction;")
    count = cursor.fetchone()[0]
    print(f"🎉 Database Ingestion Completed! Verified {count:,} successful records in 'fact_transaction' table.")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    print("==================================================")
    print("         SOUKIQ DB INGESTION ENGINE (ETL)         ")
    print("==================================================")
    try:
        create_database()
        apply_schema()
        load_all_data()
    except Exception as e:
        print(f"❌ Critical Database Error: {e}")