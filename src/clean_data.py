import pandas as pd
from pathlib import Path
import os

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
CLEANED_DIR = BASE_DIR / "data" / "cleaned"

os.makedirs(CLEANED_DIR, exist_ok=True)

print("🧹 Launching SoukIQ Data Quality & Cleaning Pipeline...")

def clean_merchants():
    print("\n🏪 Cleaning Merchants Dataset...")
    df = pd.read_csv(RAW_DIR / "merchants.csv")
    initial_rows = len(df)
    
    # 1. Standardize Text Formatting (Trim spaces & Title Case)
    df['city'] = df['city'].str.strip().str.title()
    df['store_name'] = df['store_name'].str.strip()
    df['segment'] = df['segment'].str.strip().str.title()
    
    # 2. Convert Dates
    df['join_date'] = pd.to_datetime(df['join_date']).dt.date
    
    # 3. Handle Duplicates
    df = df.drop_duplicates(subset=['merchant_id'])
    duplicates_removed = initial_rows - len(df)
    
    # Save Cleaned File
    df.to_csv(CLEANED_DIR / "merchants.csv", index=False)
    print(f"✅ Merchants Polished: {len(df):,} records validated. Purged {duplicates_removed} duplicates.")
    return df

def clean_campaigns():
    print("\n📊 Cleaning Campaigns Dataset...")
    df = pd.read_csv(RAW_DIR / "campaigns.csv")
    
    # 1. Format Dates
    df['start_date'] = pd.to_datetime(df['start_date']).dt.date
    df['end_date'] = pd.to_datetime(df['end_date']).dt.date
    
    # 2. Trim string values
    df['campaign_name'] = df['campaign_name'].str.strip()
    df['target_service'] = df['target_service'].str.strip().str.title()
    
    # Save Cleaned File
    df.to_csv(CLEANED_DIR / "campaigns.csv", index=False)
    print(f"✅ Campaigns Polished: {len(df):,} campaigns validated.")
    return df

def clean_outages():
    print("\n🔌 Cleaning Outages Dataset...")
    df = pd.read_csv(RAW_DIR / "outages.csv")
    
    # 1. Format Datetime values
    df['start_datetime'] = pd.to_datetime(df['start_datetime'])
    df['end_datetime'] = pd.to_datetime(df['end_datetime'])
    df['reason'] = df['reason'].str.strip()
    
    # Save Cleaned File
    df.to_csv(CLEANED_DIR / "outages.csv", index=False)
    print(f"✅ Outages Polished: {len(df):,} outages validated.")
    return df

def clean_transactions():
    print("\n💸 Cleaning Transactions Dataset (Core Data Quality Check)...")
    df = pd.read_csv(RAW_DIR / "transactions.csv")
    initial_rows = len(df)
    
    # 1. Handle Duplicates (e.g., accidental API double-posting)
    # If the same merchant does the exact same payment, for the same provider and amount, at the exact same second.
    df = df.drop_duplicates(subset=['merchant_id', 'transaction_datetime', 'amount_mad', 'provider'])
    duplicates_removed = initial_rows - len(df)
    
    # 2. Business Logic Validation: Amounts must be positive (Filter out anomalies)
    invalid_amounts = len(df[df['amount_mad'] <= 0])
    df = df[df['amount_mad'] > 0]
    
    # 3. Standardize Text Formats
    df['service'] = df['service'].str.strip().str.title()
    df['provider'] = df['provider'].str.strip()
    df['payment_method'] = df['payment_method'].str.strip().str.title()
    df['status'] = df['status'].str.strip().str.title()
    
    # 4. Correct Campaign IDs format for database safety (Keep as Float to preserve NaN but handle formatting)
    df['campaign_id'] = df['campaign_id'].fillna(-1).astype(int)
    # We will replace -1 back to empty value when loading into SQL or keep it as nullable
    
    # 5. Datetime normalization
    df['transaction_datetime'] = pd.to_datetime(df['transaction_datetime'])
    
    # Save Cleaned File
    df.to_csv(CLEANED_DIR / "transactions.csv", index=False)
    
    print(f"✅ Transactions Polished: {len(df):,} records validated.")
    print(f"🔍 Data Quality Details: Removed {duplicates_removed:,} POS duplicates | Removed {invalid_amounts:,} negative amount anomalies.")
    return df

if __name__ == "__main__":
    print("==================================================")
    print("         SOUKIQ ENTERPRISE DATA QUALITY            ")
    print("==================================================")
    
    clean_merchants()
    clean_campaigns()
    clean_outages()
    clean_transactions()
    
    print("\n🎉 All 4 Datasets Cleaned & Verified! Ready for PostgreSQL Import.")
    print("📂 Cleaned files are saved in 'data/cleaned/'")