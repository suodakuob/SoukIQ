import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from pathlib import Path
import os

# Base directory configuration
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

print("🚀 Starting High-Fidelity Transaction Generation Engine...")

# Set seed for reproducible statistical distributions
np.random.seed(42)
random.seed(42)

# Load existing master datasets
try:
    merchants = pd.read_csv(RAW_DIR / "merchants.csv", parse_dates=["join_date"])
    campaigns = pd.read_csv(RAW_DIR / "campaigns.csv", parse_dates=["start_date", "end_date"])
    outages = pd.read_csv(RAW_DIR / "outages.csv", parse_dates=["start_datetime", "end_datetime"])
    print(f"📊 Master Data Loaded: {len(merchants)} Merchants, {len(campaigns)} Campaigns, {len(outages)} Outages.")
except FileNotFoundError as e:
    print(f"❌ Error: Required source CSV not found. Please ensure merchants.csv, campaigns.csv, and outages.csv exist in data/raw/. Detail: {e}")
    exit(1)

# Analysis Period Definition (181 Days of H1 2026)
START_DATE = pd.Timestamp("2026-01-01")
END_DATE = pd.Timestamp("2026-06-30")
days_range = pd.date_range(START_DATE, END_DATE, freq="D")

# Business Parameters
SERVICES = ["Telecom", "Utility", "Gaming"]
PROVIDERS = {
    "Telecom": ["IAM", "Inwi", "Orange"],
    "Utility": ["Lydec", "Amendis"],
    "Gaming": ["FreeFire", "PUBG"]
}

tx_list = []

print("💸 Simulating merchant transactional activity using Poisson distributions...")

# Loop through each merchant to simulate daily transaction volume based on localized business factors
for idx, merchant in merchants.iterrows():
    m_id = merchant["merchant_id"]
    city = merchant["city"]
    segment = merchant["segment"]
    join_date = merchant["join_date"]
    
    # Define merchant transaction frequency (Lambda) and market competition decay
    # Casablanca: High density, fierce competitor multi-homing -> steady decay in merchant activity
    # Fes: Strong platform loyalty -> high stability
    # Marrakech & Agadir: Summer tourism seasonality -> spikes in Q2
    if city == "Casablanca":
        base_lambda = 2.6
        monthly_decay = 0.11 # Represents 11% volume decay per month due to competition
    elif city == "Fes":
        base_lambda = 1.3
        monthly_decay = 0.00 # 100% stable retention
    elif city in ["Marrakech", "Agadir"]:
        base_lambda = 1.1
        monthly_decay = -0.04 # Activity increases as summer approaches
    else:
        base_lambda = 1.5
        monthly_decay = 0.02
        
    for current_day in days_range:
        # Transactions can only occur on or after the merchant's onboarding (join) date
        if current_day < join_date:
            continue
            
        # Calculate active tenure in months to apply the MoM volume decay/growth
        months_active = (current_day - join_date).days / 30.4
        active_lambda = base_lambda * ((1 - monthly_decay) ** months_active)
        
        # Ensure inactive merchants maintain a nominal background probability of transacting
        active_lambda = max(0.04, active_lambda)
        
        # Determine number of transactions for the day using Poisson distribution
        daily_tx_count = np.random.poisson(active_lambda)
        
        if daily_tx_count == 0:
            continue
            
        for _ in range(daily_tx_count):
            # Ramadan 2026 Seasonality (Feb 18 to Mar 19) -> Night-shift activity patterns
            is_ramadan = (current_day >= datetime(2026, 2, 18)) & (current_day <= datetime(2026, 3, 19))
            if is_ramadan:
                hour = int(np.random.choice([20, 21, 22, 23, 0, 1, 2], p=[0.10, 0.20, 0.25, 0.20, 0.15, 0.05, 0.05]))
            else:
                # Regular business operating hours
                hour = int(np.random.choice(range(8, 22)))
                
            minute = np.random.randint(0, 60)
            second = np.random.randint(0, 60)
            txn_time = current_day.replace(hour=hour, minute=minute, second=second)
            
            # Service Mix Allocation
            service = np.random.choice(SERVICES, p=[0.70, 0.15, 0.15])
            provider = np.random.choice(PROVIDERS[service])
            
            # Dynamic basket sizes using Log-Normal distributions based on service economics
            if service == "Telecom":
                # Micro-payments (recharges)
                amount = round(np.random.lognormal(mean=2.8, sigma=0.4), 2)
                amount = max(5.00, min(amount, 100.00)) # Logical business boundaries
                commission_rate = round(np.random.uniform(0.021, 0.029), 3)
            elif service == "Utility":
                # High-value bills
                amount = round(np.random.lognormal(mean=5.3, sigma=0.3), 2)
                amount = max(50.00, min(amount, 1000.00))
                commission_rate = round(np.random.uniform(0.012, 0.018), 3)
            else: # Gaming
                # High margin gaming top-ups
                amount = round(np.random.lognormal(mean=3.8, sigma=0.4), 2)
                amount = max(10.00, min(amount, 300.00))
                commission_rate = round(np.random.uniform(0.080, 0.100), 3)
                
            # Premium merchants process 35% larger transaction baskets on average
            if segment == "Premium":
                amount = round(amount * 1.35, 2)
                
            # Wallet Adoption Evolution: Premium merchants migrate to Wallet 3x faster
            month_num = current_day.month
            wallet_probability = min(0.40, month_num * 0.06) if segment == "Premium" else min(0.12, month_num * 0.02)
            payment_method = "Wallet" if np.random.rand() < wallet_probability else "Cash"
            
            # Campaign ROI Integration
            campaign_id = None
            # Orange Recharge Campaign (Feb 1 - Feb 15) -> Spikes Orange transactions and values
            if (current_day >= datetime(2026, 2, 1)) & (current_day <= datetime(2026, 2, 15)) & (provider == "Orange"):
                campaign_id = 1
                amount = round(amount * 1.25, 2)
            # Summer Gaming Campaign (June 1 - June 30) -> Drives gaming top-ups
            elif (current_day >= datetime(2026, 6, 1)) & (current_day <= datetime(2026, 6, 30)) & (service == "Gaming"):
                campaign_id = 2
                
            tx_list.append({
                'transaction_id': "PENDING", # Populated at final sorting step
                'merchant_id': m_id,
                'transaction_datetime': txn_time,
                'service': service,
                'provider': provider,
                'amount_mad': amount,
                'commission_rate': commission_rate,
                'payment_method': payment_method,
                'status': 'Success', # Default base status
                'campaign_id': campaign_id
            })

# Convert to DataFrame
txns = pd.DataFrame(tx_list)

# Sort chronologically to preserve real timeline sequence
txns = txns.sort_values("transaction_datetime").reset_index(drop=True)

# Generate ordered and standardized Transaction IDs (TXN000001, TXN000002, ...)
txns["transaction_id"] = [f"TXN{str(i).zfill(6)}" for i in range(1, len(txns) + 1)]

# ==========================================
# 5. INJECT OUTAGE FAILURES (Operational Impact)
# ==========================================
print("🔌 Applying system outages to transactional flow...")

# Track the starting status counts
successful_before = len(txns[txns['status'] == 'Success'])

for idx, row in outages.iterrows():
    # Mask to identify transactions matching the exact downtime window and provider
    outage_mask = (txns["provider"] == row["provider"]) & \
                  (txns["transaction_datetime"] >= row["start_datetime"]) & \
                  (txns["transaction_datetime"] <= row["end_datetime"])
    
    txns.loc[outage_mask, "status"] = "Failed"

# Inject 1.5% baseline network and transactional errors (random infrastructure glitches)
baseline_failures = (txns["status"] == "Success") & (np.random.rand(len(txns)) < 0.015)
txns.loc[baseline_failures, "status"] = "Failed"

successful_after = len(txns[txns['status'] == 'Success'])
failed_txns = len(txns[txns['status'] == 'Failed'])

# Validate results
print(f"📊 Outage injection summary: Failed transactions: {failed_txns:,} | Total success: {successful_after:,}")

# Save final clean raw transactions
output_path = RAW_DIR / "transactions.csv"
txns.to_csv(output_path, index=False)

print(f"✅ H1 2026 transactions generation completed. Saved {len(txns):,} transactions to {output_path}")