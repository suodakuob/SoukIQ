from pathlib import Path
import numpy as np
import pandas as pd

# =====================================
# Project Paths
# =====================================

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

RAW_DIR.mkdir(parents=True, exist_ok=True)

# =====================================
# Reproducibility
# =====================================

np.random.seed(42)

# =====================================
# Moroccan Business Data
# =====================================

CITIES = [
    "Casablanca",
    "Rabat",
    "Marrakech",
    "Fès",
    "Agadir",
    "Tangier",
]

CITY_WEIGHTS = [
    0.40,
    0.15,
    0.15,
    0.10,
    0.10,
    0.10,
]

SEGMENTS = [
    "Standard",
    "Premium",
]

SEGMENT_WEIGHTS = [
    0.80,
    0.20,
]

# =====================================
# Generate Merchants
# =====================================

def generate_merchants(n=1000):

    merchants = pd.DataFrame({

        "merchant_id":[
            f"M{i:04d}"
            for i in range(1,n+1)
        ],

        "store_name":[
            f"Hanout {i}"
            for i in range(1,n+1)
        ],

        "city":np.random.choice(
            CITIES,
            size=n,
            p=CITY_WEIGHTS
        ),

        "join_date":pd.to_datetime("2025-10-01")+pd.to_timedelta(
            np.random.randint(0,180,n),
            unit="D"
        ),

        "segment":np.random.choice(
            SEGMENTS,
            size=n,
            p=SEGMENT_WEIGHTS
        )

    })

    return merchants


if __name__=="__main__":

    merchants=generate_merchants()

    merchants.to_csv(
        RAW_DIR/"merchants.csv",
        index=False
    )

    print("="*60)
    print("Merchants Generated")
    print("="*60)

    print(merchants.head())

    print()

    print(merchants["city"].value_counts())

    print()

    print(merchants["segment"].value_counts())