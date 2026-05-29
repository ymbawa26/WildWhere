import sys
from calendar import monthrange
from pathlib import Path
from urllib.parse import urlencode
import json
import subprocess

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.settings import RAW_FILES, TARGET_PARKS


NOAA_DAILY_SUMMARIES_URL = "https://www.ncei.noaa.gov/access/services/data/v1"
NOAA_SOURCE = "NOAA NCEI Daily Summaries"


def fetch_station_daily_summaries(
    station_id: str,
    year: int = 2024,
    month: int | None = None,
) -> pd.DataFrame:
    if month is None:
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
    else:
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-{monthrange(year, month)[1]}"

    params = {
        "dataset": "daily-summaries",
        "stations": station_id,
        "startDate": start_date,
        "endDate": end_date,
        "dataTypes": "TMAX,TMIN,PRCP",
        "format": "json",
        "units": "metric",
        "includeAttributes": "false",
    }
    url = f"{NOAA_DAILY_SUMMARIES_URL}?{urlencode(params)}"
    result = subprocess.run(
        ["curl", "-fsSL", url],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    data = json.loads(result.stdout)
    return pd.DataFrame(data)


def normalize_weather_frame(df: pd.DataFrame, park: dict) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    for column in ["TMAX", "TMIN", "PRCP"]:
        if column not in df.columns:
            df[column] = pd.NA

    normalized = pd.DataFrame(
        {
            "weather_id": park["park_code"] + "-" + df["DATE"].astype(str),
            "park_code": park["park_code"],
            "station_id": park["noaa_station_id"],
            "date": df["DATE"],
            "tmax_c": pd.to_numeric(df["TMAX"], errors="coerce"),
            "tmin_c": pd.to_numeric(df["TMIN"], errors="coerce"),
            "precipitation_mm": pd.to_numeric(df["PRCP"], errors="coerce"),
            "source": NOAA_SOURCE,
        }
    )
    return normalized.dropna(subset=["weather_id", "park_code", "station_id", "date"])


def download_weather(year: int = 2024) -> Path:
    frames = []
    for park in TARGET_PARKS:
        print(
            f"Fetching NOAA daily summaries for {park['park_name']} ({park['noaa_station_id']})...",
            flush=True,
        )
        monthly_frames = []
        for month in range(1, 13):
            monthly = fetch_station_daily_summaries(park["noaa_station_id"], year=year, month=month)
            if not monthly.empty:
                monthly_frames.append(monthly)
        df = pd.concat(monthly_frames, ignore_index=True) if monthly_frames else pd.DataFrame()
        normalized = normalize_weather_frame(df, park)
        if normalized.empty:
            raise RuntimeError(f"NOAA returned no rows for {park['park_code']} station {park['noaa_station_id']}")
        print(f"  received {len(normalized)} daily rows")
        frames.append(normalized)

    weather = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["weather_id"])
    weather.to_csv(RAW_FILES["weather"], index=False)
    print(f"Saved {len(weather):,} weather records to {RAW_FILES['weather']}")
    return RAW_FILES["weather"]


if __name__ == "__main__":
    download_weather()
