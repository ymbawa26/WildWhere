import sys
from pathlib import Path

import pandas as pd
import requests

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.settings import DATE_ACCESSED, RAW_FILES, TARGET_PARKS


NPS_STATS_URL = "https://irmaservices.nps.gov/Stats/v1/visitation"
NPS_STATS_SOURCE = "NPS Visitor Use Statistics IRMA REST API"
LICENSE_NOTE = "U.S. federal public information; verify current NPS terms before redistribution."


def _should_write(path: Path, force: bool) -> bool:
    if path.exists() and not force:
        print(f"Skipping {path.name}; file exists. Use --force to overwrite.")
        return False
    return True


def fetch_monthly_visitation(year: int = 2025) -> list[dict]:
    unit_codes = ",".join(park["park_code"] for park in TARGET_PARKS)
    response = requests.get(
        NPS_STATS_URL,
        params={
            "unitCodes": unit_codes,
            "startMonth": 1,
            "startYear": year,
            "endMonth": 12,
            "endYear": year,
            "format": "json",
        },
        timeout=45,
    )
    response.raise_for_status()
    rows = []
    for item in response.json():
        rows.append(
            {
                "park_name": item.get("UnitName"),
                "park_code": item.get("UnitCode"),
                "year": item.get("Year"),
                "month": item.get("Month"),
                "recreation_visits": item.get("RecreationVisitors"),
                "source": NPS_STATS_SOURCE,
                "source_url": NPS_STATS_URL,
                "date_accessed": DATE_ACCESSED,
                "license_usage_note": LICENSE_NOTE,
            }
        )
    return rows


def download_visitation(force: bool = False, year: int = 2025) -> Path:
    output_path = RAW_FILES["nps_visitation_monthly"]
    if not _should_write(output_path, force):
        return output_path

    print(f"NPS visitation: downloading monthly recreation visits for {year}")
    rows = fetch_monthly_visitation(year=year)
    if not rows:
        raise RuntimeError("NPS visitation API returned no records.")

    df = pd.DataFrame(rows)
    df = df.dropna(subset=["park_code", "year", "month", "recreation_visits"])
    df = df.drop_duplicates(subset=["park_code", "year", "month"])
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df):,} monthly visitation records to {output_path}")
    return output_path


if __name__ == "__main__":
    download_visitation(force=True)
