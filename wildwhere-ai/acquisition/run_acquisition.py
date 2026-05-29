import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from acquisition.gbif_client import download_gbif_occurrences
from acquisition.nps_client import download_nps_data
from acquisition.validate_raw_data import validate_all_raw_data
from acquisition.visitation_client import download_visitation
from acquisition.weather_client import download_weather
from config.settings import DOCS_DIR, RAW_DATA_DIR


def ensure_directories() -> None:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)


def run(force: bool = False) -> None:
    ensure_directories()
    print("Starting WildWhere AI Step 2 raw data acquisition...")
    print(f"Overwrite existing files: {force}")

    download_gbif_occurrences(force=force)
    download_nps_data(force=force)
    download_visitation(force=force)
    download_weather(force=force)

    print("Running raw data validation...")
    results = validate_all_raw_data()
    if any(result.failed for result in results):
        raise SystemExit("Raw data validation failed. See docs/raw_data_validation_report.md.")
    print("Step 2 acquisition and validation completed successfully.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run WildWhere AI Step 2 raw data acquisition.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing raw files.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(force=args.force)
