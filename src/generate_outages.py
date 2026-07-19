from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

RAW_DIR.mkdir(parents=True, exist_ok=True)


def generate_outages():

    outages = pd.DataFrame({

        "outage_id":[101,102,103],

        "provider":[
            "IAM",
            "Orange",
            "Inwi"
        ],

        "start_datetime":[
            "2026-05-09 18:00:00",
            "2026-06-13 18:00:00",
            "2026-06-27 18:00:00"
        ],

        "end_datetime":[
            "2026-05-09 22:00:00",
            "2026-06-13 22:00:00",
            "2026-06-27 21:00:00"
        ],

        "reason":[
            "Gateway Timeout",
            "API Overload",
            "Database Failure"
        ]

    })

    outages["start_datetime"] = pd.to_datetime(outages["start_datetime"])
    outages["end_datetime"] = pd.to_datetime(outages["end_datetime"])

    return outages


if __name__ == "__main__":

    outages = generate_outages()

    outages.to_csv(
        RAW_DIR/"outages.csv",
        index=False
    )

    print(outages)