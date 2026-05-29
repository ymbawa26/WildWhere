import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.settings import DATABASE_PATH, PROCESSED_FILES
from validation.species_eligibility import ELIGIBILITY_PATH


EXPORT_DIR = Path(__file__).resolve().parent / "exports"
EXPORT_TABLES = {
    "parks": PROCESSED_FILES["parks"],
    "species": PROCESSED_FILES["species"],
    "park_species_eligibility": ELIGIBILITY_PATH,
    "sightings": PROCESSED_FILES["sightings"],
    "weather": PROCESSED_FILES["weather"],
    "visitation": PROCESSED_FILES["visitation"],
    "wildlife_features": PROCESSED_FILES["wildlife_features"],
    "wildlife_features_enriched": PROCESSED_FILES["wildlife_features_enriched"],
}


def export_sqlite_tables() -> dict:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    exported = {}
    for table, path in EXPORT_TABLES.items():
        if not path.exists():
            print(f"Skipping {table}; missing {path}")
            continue
        df = pd.read_csv(path)
        out = EXPORT_DIR / f"{table}.csv"
        df.to_csv(out, index=False)
        exported[table] = str(out)
    if DATABASE_PATH.exists():
        with sqlite3.connect(DATABASE_PATH) as conn:
            tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table';")]
        exported["sqlite_database"] = str(DATABASE_PATH)
        exported["sqlite_tables"] = tables
    print(exported)
    return exported


if __name__ == "__main__":
    export_sqlite_tables()
