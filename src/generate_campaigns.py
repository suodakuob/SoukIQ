from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

RAW_DIR.mkdir(parents=True, exist_ok=True)


def generate_campaigns():

    campaigns = pd.DataFrame({

        "campaign_id":[1,2],

        "campaign_name":[
            "Orange Double Recharge",
            "Summer Gaming Festival"
        ],

        "start_date":[
            "2026-02-01",
            "2026-06-01"
        ],

        "end_date":[
            "2026-02-15",
            "2026-06-30"
        ],

        "target_service":[
            "Telecom",
            "Gaming"
        ],

        "budget":[
            30000,
            50000
        ]

    })

    campaigns["start_date"] = pd.to_datetime(campaigns["start_date"])
    campaigns["end_date"] = pd.to_datetime(campaigns["end_date"])

    return campaigns


if __name__ == "__main__":

    campaigns = generate_campaigns()

    campaigns.to_csv(
        RAW_DIR / "campaigns.csv",
        index=False
    )

    print(campaigns)