import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.settings import DATABASE_PATH, PROCESSED_FILES


def load_features() -> pd.DataFrame:
    path = PROCESSED_FILES["wildlife_features"]
    if not path.exists():
        raise FileNotFoundError("Missing wildlife_features.csv. Run `python etl/run_pipeline.py`.")
    return pd.read_csv(path, parse_dates=["event_date"])


def sightings_by_park(df: pd.DataFrame | None = None) -> pd.DataFrame:
    df = load_features() if df is None else df
    return (
        df.groupby("park_name", dropna=False)
        .size()
        .reset_index(name="sighting_count")
        .sort_values("sighting_count", ascending=False)
    )


def sightings_by_species(df: pd.DataFrame | None = None) -> pd.DataFrame:
    df = load_features() if df is None else df
    return (
        df.groupby(["common_name", "scientific_name"], dropna=False)
        .size()
        .reset_index(name="sighting_count")
        .sort_values("sighting_count", ascending=False)
    )


def sightings_by_season(df: pd.DataFrame | None = None) -> pd.DataFrame:
    df = load_features() if df is None else df
    order = ["winter", "spring", "summer", "fall"]
    out = df.groupby("season").size().reindex(order, fill_value=0).reset_index(name="sighting_count")
    return out


def sightings_by_time_of_day(df: pd.DataFrame | None = None) -> pd.DataFrame:
    df = load_features() if df is None else df
    return (
        df.groupby("time_of_day", dropna=False)
        .size()
        .reset_index(name="sighting_count")
        .sort_values("sighting_count", ascending=False)
    )


def top_park_species_combinations(df: pd.DataFrame | None = None, limit: int = 15) -> pd.DataFrame:
    df = load_features() if df is None else df
    return (
        df.groupby(["park_name", "common_name"], dropna=False)
        .size()
        .reset_index(name="sighting_count")
        .sort_values("sighting_count", ascending=False)
        .head(limit)
    )


def weather_during_sightings(df: pd.DataFrame | None = None) -> pd.DataFrame:
    df = load_features() if df is None else df
    weather_rows = df[df["weather_joined"].astype(bool)]
    return (
        weather_rows.groupby("common_name")
        .agg(
            sightings_with_weather=("sighting_id", "count"),
            avg_temperature_c=("temperature_avg", "mean"),
            avg_precipitation_mm=("precipitation", "mean"),
            avg_snowfall_mm=("snowfall", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("sightings_with_weather", ascending=False)
    )


def crowd_level_summary(df: pd.DataFrame | None = None) -> pd.DataFrame:
    df = load_features() if df is None else df
    joined = df[df["visitation_joined"].astype(bool)]
    return (
        joined.groupby("crowd_level", dropna=False)
        .agg(
            sighting_count=("sighting_id", "count"),
            avg_recreation_visits=("recreation_visits", "mean"),
        )
        .round(0)
        .reset_index()
        .sort_values("sighting_count", ascending=False)
    )


def data_quality_summary(df: pd.DataFrame | None = None) -> pd.DataFrame:
    df = load_features() if df is None else df
    return (
        df.groupby(["source", "data_quality_flag"], dropna=False)
        .size()
        .reset_index(name="record_count")
        .sort_values("record_count", ascending=False)
    )


def missing_value_summary(df: pd.DataFrame | None = None) -> pd.DataFrame:
    df = load_features() if df is None else df
    return pd.DataFrame(
        {
            "column": df.columns,
            "missing_count": [int(df[column].isna().sum()) for column in df.columns],
            "missing_pct": [round(float(df[column].isna().mean()), 4) for column in df.columns],
        }
    ).sort_values("missing_pct", ascending=False)


def date_range(df: pd.DataFrame | None = None) -> tuple[pd.Timestamp, pd.Timestamp]:
    df = load_features() if df is None else df
    dates = pd.to_datetime(df["event_date"], errors="coerce")
    return dates.min(), dates.max()


def save_analytics_outputs() -> dict[str, Path]:
    df = load_features()
    analytics_summary = pd.concat(
        [
            sightings_by_park(df).assign(metric_group="sightings_by_park").rename(columns={"park_name": "label"}),
            sightings_by_species(df)
            .assign(metric_group="sightings_by_species")
            .rename(columns={"common_name": "label"})[["metric_group", "label", "sighting_count"]],
            sightings_by_time_of_day(df)
            .assign(metric_group="sightings_by_time_of_day")
            .rename(columns={"time_of_day": "label"}),
        ],
        ignore_index=True,
    )
    species_park_summary = top_park_species_combinations(df, limit=1000)
    seasonal_summary = sightings_by_season(df)

    outputs = {
        "analytics_summary": PROCESSED_FILES["wildlife_features"].parent / "analytics_summary.csv",
        "species_park_summary": PROCESSED_FILES["wildlife_features"].parent / "species_park_summary.csv",
        "seasonal_summary": PROCESSED_FILES["wildlife_features"].parent / "seasonal_summary.csv",
    }
    analytics_summary.to_csv(outputs["analytics_summary"], index=False)
    species_park_summary.to_csv(outputs["species_park_summary"], index=False)
    seasonal_summary.to_csv(outputs["seasonal_summary"], index=False)
    return outputs
