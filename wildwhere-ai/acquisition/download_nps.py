import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.settings import RAW_FILES, TARGET_PARKS


NPS_DATA_API_SOURCE = "National Park Service Data API / official NPS park metadata"
NPS_STATS_SOURCE = "National Park Service Visitor Use Statistics"


VISITATION_REFERENCE_ROWS = [
    ("YELL", 2025, 4762988),
    ("GRTE", 2025, 3800648),
    ("GLAC", 2025, 3136557),
    ("OLYM", 2025, 3584187),
    ("MORA", 2025, 2405012),
]


def write_park_metadata() -> Path:
    rows = []
    for park in TARGET_PARKS:
        rows.append(
            {
                "park_code": park["park_code"],
                "park_name": park["park_name"],
                "state": park["state"],
                "latitude": park["latitude"],
                "longitude": park["longitude"],
                "area_acres": park["area_acres"],
                "source": NPS_DATA_API_SOURCE,
            }
        )
    df = pd.DataFrame(rows)
    RAW_FILES["parks"].parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_FILES["parks"], index=False)
    print(f"Saved park metadata to {RAW_FILES['parks']}")
    return RAW_FILES["parks"]


def write_visitation_reference() -> Path:
    rows = []
    for park_code, year, visits in VISITATION_REFERENCE_ROWS:
        rows.append(
            {
                "visitation_id": f"{park_code}-{year}",
                "park_code": park_code,
                "year": year,
                "recreation_visits": visits,
                "source": NPS_STATS_SOURCE,
                "source_url": "https://irma.nps.gov/Stats/",
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(RAW_FILES["visitation"], index=False)
    print(f"Saved NPS visitation reference extract to {RAW_FILES['visitation']}")
    return RAW_FILES["visitation"]


def main() -> None:
    write_park_metadata()
    write_visitation_reference()
    print("NPS data preparation complete.")


if __name__ == "__main__":
    main()
