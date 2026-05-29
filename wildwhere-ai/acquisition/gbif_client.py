import time
import sys
from pathlib import Path

import pandas as pd
import requests

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.settings import ACCEPTED_GBIF_NAME_PREFIXES, DATE_ACCESSED, RAW_FILES, TARGET_PARKS, TARGET_SPECIES


GBIF_OCCURRENCE_URL = "https://api.gbif.org/v1/occurrence/search"
GBIF_SPECIES_MATCH_URL = "https://api.gbif.org/v1/species/match"
GBIF_SOURCE = "GBIF Occurrence API"
LOCATION_FILTER_METHOD = "bounding_box"


def _should_write(path: Path, force: bool) -> bool:
    if path.exists() and not force:
        print(f"Skipping {path.name}; file exists. Use --force to overwrite.")
        return False
    return True


def resolve_species_key(scientific_name: str) -> int | None:
    response = requests.get(
        GBIF_SPECIES_MATCH_URL,
        params={"name": scientific_name, "strict": "false"},
        timeout=30,
    )
    response.raise_for_status()
    match = response.json()
    return match.get("usageKey")


def fetch_occurrences_for_species_and_park(
    species: dict,
    scientific_name: str,
    park: dict,
    page_limit: int = 300,
    max_records: int = 120,
) -> list[dict]:
    species_key = resolve_species_key(scientific_name)
    if not species_key:
        print(f"  Warning: GBIF could not resolve species key for {scientific_name}")
        return []

    records = []
    offset = 0
    while offset < max_records:
        limit = min(page_limit, max_records - offset)
        params = {
            "country": "US",
            "hasCoordinate": "true",
            "hasGeospatialIssue": "false",
            "taxonKey": species_key,
            "geometry": park["gbif_geometry"],
            "limit": limit,
            "offset": offset,
        }
        response = requests.get(GBIF_OCCURRENCE_URL, params=params, timeout=45)
        response.raise_for_status()
        payload = response.json()
        batch = payload.get("results", [])
        if not batch:
            break

        for item in batch:
            occurrence_key = item.get("key")
            returned_name = item.get("scientificName") or ""
            is_target_name = any(returned_name.startswith(name) for name in ACCEPTED_GBIF_NAME_PREFIXES)
            if not occurrence_key or not is_target_name:
                continue
            records.append(
                {
                    "occurrence_id": f"GBIF-{occurrence_key}",
                    "gbif_id": occurrence_key,
                    "query_scientific_name": scientific_name,
                    "gbif_species_key": species_key,
                    "park_code": park["park_code"],
                    "park_name": park["park_name"],
                    "target_common_name": species["common_name"],
                    "scientific_name": returned_name,
                    "common_name": item.get("vernacularName"),
                    "event_date": item.get("eventDate") or item.get("dateIdentified"),
                    "decimal_latitude": item.get("decimalLatitude"),
                    "decimal_longitude": item.get("decimalLongitude"),
                    "basis_of_record": item.get("basisOfRecord"),
                    "dataset_name": item.get("datasetName"),
                    "institution_code": item.get("institutionCode"),
                    "country": item.get("country"),
                    "state_province": item.get("stateProvince"),
                    "coordinate_uncertainty": item.get("coordinateUncertaintyInMeters"),
                    "license": item.get("license"),
                    "source": GBIF_SOURCE,
                    "source_url": GBIF_OCCURRENCE_URL,
                    "date_accessed": DATE_ACCESSED,
                    "location_filter_method": LOCATION_FILTER_METHOD,
                }
            )

        offset += len(batch)
        if payload.get("endOfRecords") or len(batch) < limit:
            break
        time.sleep(0.2)
    return records


def download_gbif_occurrences(force: bool = False) -> Path:
    output_path = RAW_FILES["gbif_occurrences"]
    if not _should_write(output_path, force):
        return output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for park in TARGET_PARKS:
        print(f"GBIF: querying near {park['park_name']} with bounding box filter")
        for species in TARGET_SPECIES:
            for scientific_name in species["scientific_names"]:
                species_rows = fetch_occurrences_for_species_and_park(species, scientific_name, park)
                print(f"  {species['common_name']} / {scientific_name}: {len(species_rows)} records")
                rows.extend(species_rows)

    if not rows:
        raise RuntimeError("GBIF acquisition returned no occurrence records.")

    df = pd.DataFrame(rows).drop_duplicates(subset=["occurrence_id", "park_code"])
    df = df.dropna(subset=["occurrence_id", "scientific_name", "decimal_latitude", "decimal_longitude"])
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df):,} GBIF occurrence records to {output_path}")
    return output_path


if __name__ == "__main__":
    download_gbif_occurrences(force=True)
