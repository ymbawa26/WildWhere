import re
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.settings import PROCESSED_FILES, TARGET_SPECIES


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")


TARGET_COMMON_TO_ID = {
    species["common_name"]: f"species_{_slug(species['common_name'])}"
    for species in TARGET_SPECIES
}


def _snake_case_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = {
        column: re.sub(r"[^a-z0-9]+", "_", str(column).strip().lower()).strip("_")
        for column in df.columns
    }
    return df.rename(columns=renamed)


def _strip_text(df: pd.DataFrame) -> pd.DataFrame:
    for column in df.select_dtypes(include=["object"]).columns:
        df[column] = df[column].map(lambda value: value.strip() if isinstance(value, str) else value)
    return df


def _season(month: int | float) -> str | None:
    if pd.isna(month):
        return None
    month = int(month)
    if month in {12, 1, 2}:
        return "winter"
    if month in {3, 4, 5}:
        return "spring"
    if month in {6, 7, 8}:
        return "summer"
    if month in {9, 10, 11}:
        return "fall"
    return None


def _time_of_day(timestamp) -> str:
    if pd.isna(timestamp) or timestamp.hour == 0 and timestamp.minute == 0 and timestamp.second == 0:
        return "unknown"
    hour = timestamp.hour
    if 5 <= hour < 8:
        return "early_morning"
    if 8 <= hour < 12:
        return "morning"
    if 12 <= hour < 17:
        return "afternoon"
    if 17 <= hour < 21:
        return "evening"
    return "night"


def _canonical_common_name(value: str) -> str:
    value = str(value).strip()
    mapping = {
        "Grizzly Bear": "Grizzly Bear",
        "Black Bear": "Black Bear",
        "Moose": "Moose",
        "Elk": "Elk",
        "Bison": "Bison",
        "Gray Wolf": "Gray Wolf",
        "Mountain Goat": "Mountain Goat",
        "Bighorn Sheep": "Bighorn Sheep",
        "Bald Eagle": "Bald Eagle",
        "Coyote": "Coyote",
    }
    return mapping.get(value, value.title())


def clean_parks(df: pd.DataFrame) -> pd.DataFrame:
    df = _strip_text(_snake_case_columns(df.copy())).drop_duplicates()
    df["park_code"] = df["park_code"].str.upper()
    df["park_id"] = "park_" + df["park_code"].str.lower()
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["acres"] = pd.to_numeric(df["acres"], errors="coerce")
    columns = [
        "park_id",
        "park_code",
        "park_name",
        "state",
        "latitude",
        "longitude",
        "acres",
        "designation",
        "official_url",
        "source",
    ]
    return df.dropna(subset=["park_id", "park_code", "park_name", "latitude", "longitude"])[columns]


def clean_species(df: pd.DataFrame) -> pd.DataFrame:
    source_df = _strip_text(_snake_case_columns(df.copy())).drop_duplicates()
    rows = []
    for species in TARGET_SPECIES:
        common_name = _canonical_common_name(species["common_name"])
        scientific_name = species["scientific_names"][0]
        matches = source_df[
            source_df["scientific_name"].fillna("").str.lower().isin(
                [name.lower() for name in species["scientific_names"]]
            )
        ]
        category = matches["category"].dropna().iloc[0] if not matches.empty else None
        source = "; ".join(sorted(matches["source"].dropna().unique())) if not matches.empty else "Target species configuration"
        rows.append(
            {
                "species_id": f"species_{_slug(common_name)}",
                "common_name": common_name,
                "scientific_name": scientific_name,
                "category": category,
                "source": source,
            }
        )
    return pd.DataFrame(rows).drop_duplicates(subset=["species_id"])


def _quality_flag(row: pd.Series) -> str:
    uncertainty = row.get("coordinate_uncertainty")
    if pd.notna(uncertainty) and float(uncertainty) > 10000:
        return "coordinate_uncertain"
    if row.get("location_filter_method") == "bounding_box":
        return "bounding_box_only"
    if row.get("time_of_day") == "unknown":
        return "missing_time"
    if pd.isna(row.get("dataset_name")) or pd.isna(row.get("institution_code")):
        return "limited_metadata"
    return "high_confidence"


def clean_sightings(df: pd.DataFrame, parks: pd.DataFrame, species: pd.DataFrame) -> pd.DataFrame:
    df = _strip_text(_snake_case_columns(df.copy())).drop_duplicates()
    before = len(df)
    df["parsed_event_datetime"] = pd.to_datetime(df["event_date"], errors="coerce", utc=True)
    df["event_date"] = df["parsed_event_datetime"].dt.date.astype("string")
    df["year"] = df["parsed_event_datetime"].dt.year
    df["month"] = df["parsed_event_datetime"].dt.month
    df["season"] = df["month"].map(_season)
    df["time_of_day"] = df["parsed_event_datetime"].map(_time_of_day)
    df["decimal_latitude"] = pd.to_numeric(df["decimal_latitude"], errors="coerce")
    df["decimal_longitude"] = pd.to_numeric(df["decimal_longitude"], errors="coerce")
    df["coordinate_uncertainty"] = pd.to_numeric(df["coordinate_uncertainty"], errors="coerce")
    df["park_code"] = df["park_code"].str.upper()
    df["park_id"] = df["park_code"].map(dict(zip(parks["park_code"], parks["park_id"])))
    df["common_name"] = df["target_common_name"].map(_canonical_common_name)
    df["species_id"] = df["common_name"].map(TARGET_COMMON_TO_ID)
    df["sighting_id"] = df["occurrence_id"].astype(str) + "_" + df["park_id"].astype(str)
    df["data_quality_flag"] = df.apply(_quality_flag, axis=1)

    df = df.dropna(
        subset=[
            "occurrence_id",
            "park_id",
            "species_id",
            "event_date",
            "decimal_latitude",
            "decimal_longitude",
        ]
    )
    df = df.drop_duplicates(subset=["sighting_id"])
    df.attrs["dropped_records"] = before - len(df)
    columns = [
        "sighting_id",
        "occurrence_id",
        "park_id",
        "species_id",
        "scientific_name",
        "common_name",
        "event_date",
        "year",
        "month",
        "season",
        "time_of_day",
        "decimal_latitude",
        "decimal_longitude",
        "coordinate_uncertainty",
        "basis_of_record",
        "location_filter_method",
        "source",
        "license",
        "data_quality_flag",
    ]
    return df[columns]


def clean_weather(df: pd.DataFrame, parks: pd.DataFrame) -> pd.DataFrame:
    df = _strip_text(_snake_case_columns(df.copy())).drop_duplicates()
    df["park_code"] = df["park_code"].str.upper()
    df["park_id"] = df["park_code"].map(dict(zip(parks["park_code"], parks["park_id"])))
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date.astype("string")
    for column in ["temperature_max", "temperature_min", "precipitation", "snowfall", "wind_speed"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df["temperature_avg"] = (df["temperature_max"] + df["temperature_min"]) / 2
    df["weather_id"] = df["park_id"].astype(str) + "_" + df["station_id"].astype(str) + "_" + df["date"].astype(str)
    columns = [
        "weather_id",
        "park_id",
        "station_id",
        "date",
        "temperature_max",
        "temperature_min",
        "temperature_avg",
        "precipitation",
        "snowfall",
        "wind_speed",
        "source",
    ]
    return df.dropna(subset=["weather_id", "park_id", "station_id", "date"])[columns].drop_duplicates(subset=["weather_id"])


def clean_visitation(df: pd.DataFrame, parks: pd.DataFrame) -> pd.DataFrame:
    df = _strip_text(_snake_case_columns(df.copy())).drop_duplicates()
    df["park_code"] = df["park_code"].str.upper()
    df["park_id"] = df["park_code"].map(dict(zip(parks["park_code"], parks["park_id"])))
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["month"] = pd.to_numeric(df["month"], errors="coerce").astype("Int64")
    df["recreation_visits"] = pd.to_numeric(df["recreation_visits"], errors="coerce")
    df = df[(df["month"].between(1, 12)) & (df["recreation_visits"] >= 0)].copy()

    def label_crowds(group: pd.DataFrame) -> pd.Series:
        ranks = group["recreation_visits"].rank(method="first", pct=True)
        return pd.cut(
            ranks,
            bins=[0, 1 / 3, 2 / 3, 1],
            labels=["low", "medium", "high"],
            include_lowest=True,
        ).astype(str)

    df["crowd_level"] = df.groupby("park_id", group_keys=False).apply(label_crowds, include_groups=False)
    df["visit_id"] = df["park_id"].astype(str) + "_" + df["year"].astype(str) + "_" + df["month"].astype(str).str.zfill(2)
    columns = [
        "visit_id",
        "park_id",
        "park_name",
        "year",
        "month",
        "recreation_visits",
        "crowd_level",
        "source",
    ]
    return df.dropna(subset=["visit_id", "park_id", "year", "month"])[columns].drop_duplicates(subset=["visit_id"])


def create_wildlife_features(cleaned_dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    sightings = cleaned_dfs["sightings"].copy()
    parks = cleaned_dfs["parks"].copy()
    species = cleaned_dfs["species"].copy()
    weather = cleaned_dfs["weather"].copy()
    visitation = cleaned_dfs["visitation"].copy()

    features = sightings.merge(
        parks[["park_id", "park_name", "state"]],
        on="park_id",
        how="left",
    )
    features = features.merge(
        species[["species_id", "category"]],
        on="species_id",
        how="left",
    )
    features = features.merge(
        weather[
            [
                "park_id",
                "date",
                "temperature_max",
                "temperature_min",
                "temperature_avg",
                "precipitation",
                "snowfall",
                "wind_speed",
            ]
        ],
        left_on=["park_id", "event_date"],
        right_on=["park_id", "date"],
        how="left",
    )
    features["weather_joined"] = features["date"].notna()
    features = features.drop(columns=["date"])
    features = features.merge(
        visitation[["park_id", "year", "month", "recreation_visits", "crowd_level"]],
        on=["park_id", "year", "month"],
        how="left",
    )
    features["visitation_joined"] = features["recreation_visits"].notna()
    features["source"] = features["source"].fillna("GBIF Occurrence API")
    columns = [
        "sighting_id",
        "park_id",
        "park_name",
        "state",
        "species_id",
        "common_name",
        "scientific_name",
        "category",
        "event_date",
        "year",
        "month",
        "season",
        "time_of_day",
        "decimal_latitude",
        "decimal_longitude",
        "coordinate_uncertainty",
        "temperature_max",
        "temperature_min",
        "temperature_avg",
        "precipitation",
        "snowfall",
        "wind_speed",
        "recreation_visits",
        "crowd_level",
        "basis_of_record",
        "location_filter_method",
        "data_quality_flag",
        "source",
        "weather_joined",
        "visitation_joined",
    ]
    return features[columns]


def transform_all(raw_dfs: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    parks = clean_parks(raw_dfs["parks"])
    species = clean_species(raw_dfs["species"])
    sightings = clean_sightings(raw_dfs["sightings"], parks, species)
    weather = clean_weather(raw_dfs["weather"], parks)
    visitation = clean_visitation(raw_dfs["visitation"], parks)
    cleaned = {
        "parks": parks,
        "species": species,
        "sightings": sightings,
        "weather": weather,
        "visitation": visitation,
    }
    cleaned["wildlife_features"] = create_wildlife_features(cleaned)
    return cleaned


def write_processed_data(cleaned_dfs: dict[str, pd.DataFrame]) -> None:
    PROCESSED_FILES["parks"].parent.mkdir(parents=True, exist_ok=True)
    for name, df in cleaned_dfs.items():
        df.to_csv(PROCESSED_FILES[name], index=False)
        print(f"Wrote {len(df):,} rows to {PROCESSED_FILES[name]}")
