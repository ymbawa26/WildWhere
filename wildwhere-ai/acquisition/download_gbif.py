import sys
from pathlib import Path

import pandas as pd
import requests

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.settings import RAW_FILES, TARGET_PARKS


GBIF_OCCURRENCE_URL = "https://api.gbif.org/v1/occurrence/search"
GBIF_SOURCE = "GBIF Occurrence API"


def fetch_park_occurrences(park: dict, limit: int = 120) -> list[dict]:
    params = {
        "country": "US",
        "hasCoordinate": "true",
        "hasGeospatialIssue": "false",
        "basisOfRecord": "HUMAN_OBSERVATION",
        "geometry": park["gbif_geometry"],
        "limit": limit,
    }
    response = requests.get(GBIF_OCCURRENCE_URL, params=params, timeout=45)
    response.raise_for_status()
    records = response.json().get("results", [])

    cleaned = []
    for item in records:
        if not item.get("key") or not item.get("scientificName"):
            continue
        cleaned.append(
            {
                "sighting_id": f"GBIF-{item.get('key')}",
                "park_code": park["park_code"],
                "gbif_id": item.get("key"),
                "scientific_name": item.get("scientificName"),
                "common_name": item.get("vernacularName"),
                "taxon_rank": item.get("taxonRank"),
                "event_date": item.get("eventDate") or item.get("dateIdentified"),
                "decimal_latitude": item.get("decimalLatitude"),
                "decimal_longitude": item.get("decimalLongitude"),
                "basis_of_record": item.get("basisOfRecord"),
                "dataset_key": item.get("datasetKey"),
                "recorded_by": "; ".join(item.get("recordedBy", []))
                if isinstance(item.get("recordedBy"), list)
                else item.get("recordedBy"),
                "source": GBIF_SOURCE,
            }
        )
    return cleaned


def download_gbif_occurrences() -> Path:
    all_records: list[dict] = []
    for park in TARGET_PARKS:
        print(f"Fetching GBIF records for {park['park_name']}...")
        records = fetch_park_occurrences(park)
        print(f"  received {len(records)} usable records")
        all_records.extend(records)

    if not all_records:
        raise RuntimeError("No GBIF occurrence records were returned.")

    df = pd.DataFrame(all_records).drop_duplicates(subset=["sighting_id"])
    critical = ["sighting_id", "park_code", "scientific_name", "decimal_latitude", "decimal_longitude"]
    df = df.dropna(subset=critical)
    RAW_FILES["sightings"].parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_FILES["sightings"], index=False)
    print(f"Saved {len(df):,} wildlife sighting records to {RAW_FILES['sightings']}")
    print(df.groupby("park_code").size().to_string())
    return RAW_FILES["sightings"]


if __name__ == "__main__":
    download_gbif_occurrences()
