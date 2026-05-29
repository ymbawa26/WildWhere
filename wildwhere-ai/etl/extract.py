import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.settings import RAW_FILES, REQUIRED_COLUMNS


class RawDataError(RuntimeError):
    """Raised when a raw input file is missing or malformed."""


def _load_raw_csv(dataset_name: str) -> pd.DataFrame:
    path = RAW_FILES[dataset_name]
    if not path.exists():
        raise RawDataError(
            f"Missing raw dataset `{dataset_name}` at {path}. "
            "Run `python acquisition/run_acquisition.py` before the ETL pipeline."
        )
    try:
        df = pd.read_csv(path)
    except Exception as exc:
        raise RawDataError(f"Could not read raw dataset `{dataset_name}` at {path}: {exc}") from exc

    required = set(REQUIRED_COLUMNS[dataset_name])
    missing = sorted(required - set(df.columns))
    if missing:
        raise RawDataError(f"Raw dataset `{dataset_name}` is missing required columns: {missing}")
    return df


def load_raw_parks() -> pd.DataFrame:
    return _load_raw_csv("nps_parks")


def load_raw_species() -> pd.DataFrame:
    return _load_raw_csv("nps_species_reference")


def load_raw_sightings() -> pd.DataFrame:
    return _load_raw_csv("gbif_occurrences")


def load_raw_weather() -> pd.DataFrame:
    return _load_raw_csv("noaa_weather_daily")


def load_raw_visitation() -> pd.DataFrame:
    return _load_raw_csv("nps_visitation_monthly")


def load_all_raw_data() -> dict[str, pd.DataFrame]:
    return {
        "parks": load_raw_parks(),
        "species": load_raw_species(),
        "sightings": load_raw_sightings(),
        "weather": load_raw_weather(),
        "visitation": load_raw_visitation(),
    }
