import json
import sys
import subprocess
import time
from calendar import monthrange
from pathlib import Path
from urllib.parse import urlencode

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.settings import DATE_ACCESSED, RAW_FILES, TARGET_PARKS


NOAA_DAILY_SUMMARIES_URL = "https://www.ncei.noaa.gov/access/services/data/v1"
NOAA_SOURCE = "NOAA NCEI Daily Summaries"
LICENSE_NOTE = "NOAA/NCEI public data; verify dataset-specific terms before redistribution."


def _should_write(path: Path, force: bool) -> bool:
    if path.exists() and not force:
        print(f"Skipping {path.name}; file exists. Use --force to overwrite.")
        return False
    return True


def _fetch_month(station_id: str, year: int, month: int) -> pd.DataFrame:
    params = {
        "dataset": "daily-summaries",
        "stations": station_id,
        "startDate": f"{year}-{month:02d}-01",
        "endDate": f"{year}-{month:02d}-{monthrange(year, month)[1]}",
        "dataTypes": "TMAX,TMIN,PRCP,SNOW,AWND",
        "format": "json",
        "units": "metric",
        "includeAttributes": "false",
    }
    url = f"{NOAA_DAILY_SUMMARIES_URL}?{urlencode(params)}"
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            result = subprocess.run(
                ["curl", "-fsSL", url],
                check=True,
                capture_output=True,
                text=True,
                timeout=90,
            )
            return pd.DataFrame(json.loads(result.stdout))
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            last_error = exc
            print(f"  NOAA retry {attempt}/3 for {station_id} {year}-{month:02d}")
            time.sleep(2 * attempt)
    raise RuntimeError(f"NOAA request failed for {station_id} {year}-{month:02d}: {last_error}")


def _normalize_weather(df: pd.DataFrame, park: dict) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    for column in ["TMAX", "TMIN", "PRCP", "SNOW", "AWND"]:
        if column not in df.columns:
            df[column] = pd.NA
    return pd.DataFrame(
        {
            "station_id": park["noaa_station_id"],
            "nearest_park": park["park_name"],
            "park_code": park["park_code"],
            "date": df["DATE"],
            "temperature_max": pd.to_numeric(df["TMAX"], errors="coerce"),
            "temperature_min": pd.to_numeric(df["TMIN"], errors="coerce"),
            "precipitation": pd.to_numeric(df["PRCP"], errors="coerce"),
            "snowfall": pd.to_numeric(df["SNOW"], errors="coerce"),
            "wind_speed": pd.to_numeric(df["AWND"], errors="coerce"),
            "source": NOAA_SOURCE,
            "source_url": NOAA_DAILY_SUMMARIES_URL,
            "date_accessed": DATE_ACCESSED,
            "license_usage_note": LICENSE_NOTE,
        }
    )


def write_station_mapping(force: bool = False) -> Path:
    output_path = RAW_FILES["weather_station_mapping"]
    if not _should_write(output_path, force):
        return output_path

    rows = [
        {
            "park_code": park["park_code"],
            "park_name": park["park_name"],
            "station_id": park["noaa_station_id"],
            "station_name": park["noaa_station_name"],
            "distance_km": park["weather_station_distance_km"],
            "selection_method": "nearest representative station with available 2024 daily summaries",
            "source": NOAA_SOURCE,
            "source_url": NOAA_DAILY_SUMMARIES_URL,
            "date_accessed": DATE_ACCESSED,
            "license_usage_note": LICENSE_NOTE,
        }
        for park in TARGET_PARKS
    ]
    pd.DataFrame(rows).to_csv(output_path, index=False)
    print(f"Saved weather station mapping to {output_path}")
    return output_path


def download_weather(force: bool = False, year: int = 2024) -> list[Path]:
    weather_path = RAW_FILES["noaa_weather_daily"]
    mapping_path = write_station_mapping(force=force)
    if not _should_write(weather_path, force):
        return [weather_path, mapping_path]

    frames = []
    for park in TARGET_PARKS:
        print(f"NOAA: downloading {year} daily summaries for {park['park_name']} ({park['noaa_station_id']})")
        monthly_frames = []
        for month in range(1, 13):
            month_df = _fetch_month(park["noaa_station_id"], year, month)
            if not month_df.empty:
                monthly_frames.append(month_df)
        if not monthly_frames:
            raise RuntimeError(f"No NOAA weather records returned for {park['park_code']}")
        normalized = _normalize_weather(pd.concat(monthly_frames, ignore_index=True), park)
        print(f"  received {len(normalized)} daily records")
        frames.append(normalized)

    weather = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["park_code", "station_id", "date"])
    weather.to_csv(weather_path, index=False)
    print(f"Saved {len(weather):,} NOAA daily weather records to {weather_path}")
    return [weather_path, mapping_path]


if __name__ == "__main__":
    download_weather(force=True)
