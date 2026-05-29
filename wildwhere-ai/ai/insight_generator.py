import os
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from ai.explanation_templates import BOUNDING_BOX_NOTE, PROJECT_CAVEAT, SPARSE_DATA_NOTE
from config.settings import PROCESSED_FILES


def _load_features() -> pd.DataFrame:
    return pd.read_csv(PROCESSED_FILES["wildlife_features"], parse_dates=["event_date"])


def generate_species_insight(species: str, park: str) -> str:
    df = _load_features()
    subset = df[(df["common_name"] == species) & (df["park_name"] == park)]
    if subset.empty:
        return f"No processed records were found for {species} in {park}. {PROJECT_CAVEAT}"
    top_season = subset["season"].value_counts().idxmax()
    top_time = subset["time_of_day"].value_counts().idxmax()
    count = len(subset)
    note = SPARSE_DATA_NOTE if count < 20 else BOUNDING_BOX_NOTE
    return (
        f"Reported {species} observations in {park} are strongest in {top_season} during {top_time.replace('_', ' ')} "
        f"within the processed dataset ({count} records). {note} {PROJECT_CAVEAT}"
    )


def generate_park_summary(park: str) -> str:
    df = _load_features()
    subset = df[df["park_name"] == park]
    if subset.empty:
        return f"No processed wildlife records were found for {park}. {PROJECT_CAVEAT}"
    top_species = subset["common_name"].value_counts().idxmax()
    count = len(subset)
    species_count = subset["common_name"].nunique()
    return (
        f"{park} has {count} processed reported observations across {species_count} target species. "
        f"The most common target species in this dataset is {top_species}. {PROJECT_CAVEAT}"
    )


def generate_data_quality_note() -> str:
    df = _load_features()
    weather_rate = df["weather_joined"].astype(bool).mean()
    visitation_rate = df["visitation_joined"].astype(bool).mean()
    flags = df["data_quality_flag"].value_counts().to_dict()
    dominant_flag = max(flags, key=flags.get)
    return (
        f"Data quality is strongest as a transparent historical observation layer: weather joined for {weather_rate:.1%} "
        f"of records and visitation joined for {visitation_rate:.1%}. The most common data quality flag is "
        f"{dominant_flag.replace('_', ' ')}. {BOUNDING_BOX_NOTE}"
    )


def generate_prediction_explanation(prediction_result: dict) -> str:
    category = prediction_result.get("predicted_category", "unknown")
    confidence = prediction_result.get("confidence", 0)
    features = prediction_result.get("feature_summary", {})
    return (
        f"The model estimates a {category} historical reported-sighting likelihood with {confidence:.1%} confidence "
        f"for {features.get('common_name', 'the selected species')} in {features.get('park_name', 'the selected park')} "
        f"during {features.get('season', 'the selected season')}. This is a pattern estimate based on public records. {PROJECT_CAVEAT}"
    )


def optional_openai_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))
