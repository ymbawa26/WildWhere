import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.settings import PROCESSED_DATA_DIR, RAW_FILES, TARGET_PARKS, TARGET_SPECIES


ELIGIBILITY_PATH = PROCESSED_DATA_DIR / "park_species_eligibility.csv"
ALLOWED_STATUSES = {"present", "probably present"}


def _target_species_rows() -> list[dict]:
    rows = []
    for species in TARGET_SPECIES:
        for scientific_name in species["scientific_names"]:
            rows.append(
                {
                    "common_name": species["common_name"],
                    "scientific_name": scientific_name,
                }
            )
    return rows


def build_park_species_eligibility() -> pd.DataFrame:
    nps = pd.read_csv(RAW_FILES["nps_species_reference"])
    nps["scientific_name_key"] = nps["scientific_name"].fillna("").str.lower()
    rows = []
    for park in TARGET_PARKS:
        park_code = park["park_code"]
        park_name = park["park_name"]
        park_nps = nps[nps["park_code"] == park_code]
        for species in TARGET_SPECIES:
            names = [name.lower() for name in species["scientific_names"]]
            matches = park_nps[park_nps["scientific_name_key"].isin(names)]
            allowed_matches = matches[
                matches["occurrence_status"].fillna("").str.lower().isin(ALLOWED_STATUSES)
            ]
            if not matches.empty:
                best = allowed_matches.iloc[0] if not allowed_matches.empty else matches.iloc[0]
                status = str(best.get("occurrence_status") or "Unknown")
                is_documented = status.lower() in ALLOWED_STATUSES
                confidence = "high" if status.lower() == "present" else "medium" if is_documented else "blocked"
                notes = f"NPSpecies occurrence status: {status}"
                scientific_name = best.get("scientific_name") or species["scientific_names"][0]
                source = best.get("source") or "NPSpecies"
            else:
                is_documented = False
                confidence = "blocked"
                notes = "No matching NPSpecies target-species record for this park."
                scientific_name = species["scientific_names"][0]
                source = "NPSpecies"
            rows.append(
                {
                    "park_name": park_name,
                    "park_code": park_code,
                    "common_name": species["common_name"],
                    "scientific_name": scientific_name,
                    "is_documented_in_park": bool(is_documented),
                    "source": source,
                    "confidence_level": confidence,
                    "notes": notes,
                }
            )
    df = pd.DataFrame(rows)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(ELIGIBILITY_PATH, index=False)
    print(f"Wrote {len(df)} park-species eligibility rows to {ELIGIBILITY_PATH}")
    return df


def load_eligibility() -> pd.DataFrame:
    if not ELIGIBILITY_PATH.exists():
        return build_park_species_eligibility()
    return pd.read_csv(ELIGIBILITY_PATH)


def is_species_eligible(park_name: str, common_name: str) -> dict:
    df = load_eligibility()
    match = df[
        (df["park_name"].str.lower() == str(park_name).lower())
        & (df["common_name"].str.lower() == str(common_name).lower())
    ]
    if match.empty:
        return {
            "park_exists": park_name in set(df["park_name"]),
            "species_exists": common_name in set(df["common_name"]),
            "is_documented_in_park": False,
            "message": "This park/species combination is not in the project reference table.",
        }
    row = match.iloc[0].to_dict()
    row["is_documented_in_park"] = bool(row["is_documented_in_park"])
    row["message"] = (
        "This species is documented for the selected park in the project's reference data."
        if row["is_documented_in_park"]
        else "This species is not documented for the selected park in the project's reference data."
    )
    return row


if __name__ == "__main__":
    build_park_species_eligibility()
