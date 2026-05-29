import os
import sys
from pathlib import Path

import pandas as pd
import requests

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.settings import DATE_ACCESSED, RAW_FILES, TARGET_PARKS


NPS_API_URL = "https://developer.nps.gov/api/v1/parks"
NPSPECIES_URL_TEMPLATE = "https://irmaservices.nps.gov/NPSpecies/v3/rest/detaillist/{park_code}/mammals,birds"
NPS_PARKS_SOURCE = "National Park Service park reference"
NPS_SPECIES_SOURCE = "NPSpecies IRMA REST API"
LICENSE_NOTE = "U.S. federal public information; verify current NPS terms before redistribution."


def _should_write(path: Path, force: bool) -> bool:
    if path.exists() and not force:
        print(f"Skipping {path.name}; file exists. Use --force to overwrite.")
        return False
    return True


def _park_from_config(park: dict) -> dict:
    return {
        "park_code": park["park_code"],
        "park_name": park["park_name"],
        "state": park["state"],
        "latitude": park["latitude"],
        "longitude": park["longitude"],
        "acres": park["area_acres"],
        "designation": park["designation"],
        "description": park["description"],
        "official_url": park["official_url"],
        "source": NPS_PARKS_SOURCE,
        "source_url": park["official_url"],
        "date_accessed": DATE_ACCESSED,
        "license_usage_note": LICENSE_NOTE,
    }


def download_park_metadata(force: bool = False) -> Path:
    output_path = RAW_FILES["nps_parks"]
    if not _should_write(output_path, force):
        return output_path

    api_key = os.getenv("NPS_API_KEY")
    rows = []
    if api_key:
        print("NPS parks: using NPS developer API with NPS_API_KEY.")
        park_codes = ",".join(park["park_code"].lower() for park in TARGET_PARKS)
        response = requests.get(
            NPS_API_URL,
            params={"parkCode": park_codes, "limit": 10, "api_key": api_key},
            timeout=30,
        )
        response.raise_for_status()
        by_code = {item.get("parkCode", "").upper(): item for item in response.json().get("data", [])}
        for park in TARGET_PARKS:
            item = by_code.get(park["park_code"])
            if not item:
                rows.append(_park_from_config(park))
                continue
            rows.append(
                {
                    "park_code": park["park_code"],
                    "park_name": item.get("fullName") or park["park_name"],
                    "state": item.get("states") or park["state"],
                    "latitude": item.get("latitude") or park["latitude"],
                    "longitude": item.get("longitude") or park["longitude"],
                    "acres": park["area_acres"],
                    "designation": item.get("designation") or park["designation"],
                    "description": item.get("description") or park["description"],
                    "official_url": item.get("url") or park["official_url"],
                    "source": "NPS Developer API",
                    "source_url": NPS_API_URL,
                    "date_accessed": DATE_ACCESSED,
                    "license_usage_note": LICENSE_NOTE,
                }
            )
    else:
        print("NPS parks: NPS_API_KEY not set; using official NPS reference fields from project config.")
        rows = [_park_from_config(park) for park in TARGET_PARKS]

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df):,} park metadata records to {output_path}")
    return output_path


def fetch_species_for_park(park: dict) -> list[dict]:
    url = NPSPECIES_URL_TEMPLATE.format(park_code=park["park_code"])
    response = requests.get(url, params={"format": "json"}, timeout=45)
    response.raise_for_status()
    species_rows = response.json()
    rows = []
    for item in species_rows:
        rows.append(
            {
                "park_name": park["park_name"],
                "park_code": park["park_code"],
                "category": item.get("Category"),
                "common_name": item.get("CommonNames"),
                "scientific_name": item.get("ScientificName"),
                "occurrence_status": item.get("Occurrence"),
                "abundance": item.get("Abundance"),
                "nativeness": item.get("Nativeness"),
                "record_status": item.get("RecordStatus"),
                "source": NPS_SPECIES_SOURCE,
                "source_url": url,
                "date_accessed": DATE_ACCESSED,
                "license_usage_note": LICENSE_NOTE,
            }
        )
    return rows


def download_species_reference(force: bool = False) -> Path:
    output_path = RAW_FILES["nps_species_reference"]
    if not _should_write(output_path, force):
        return output_path

    rows = []
    for park in TARGET_PARKS:
        print(f"NPSpecies: downloading mammal and bird list for {park['park_name']}")
        park_rows = fetch_species_for_park(park)
        print(f"  received {len(park_rows)} species records")
        rows.extend(park_rows)

    if not rows:
        raise RuntimeError("NPSpecies acquisition returned no records.")

    df = pd.DataFrame(rows).dropna(subset=["park_code", "scientific_name"])
    df = df.drop_duplicates(subset=["park_code", "scientific_name"])
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df):,} NPS species reference records to {output_path}")
    return output_path


def download_nps_data(force: bool = False) -> list[Path]:
    return [download_park_metadata(force=force), download_species_reference(force=force)]


if __name__ == "__main__":
    download_nps_data(force=True)
