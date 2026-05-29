import json
from pathlib import Path

import joblib
import pandas as pd

MODEL_DIR = Path(__file__).resolve().parent
MODEL_PATH = MODEL_DIR / "wildlife_model.pkl"
METRICS_PATH = MODEL_DIR / "model_metrics.json"

CATEGORICAL_FEATURES = [
    "park_name",
    "common_name",
    "season",
    "time_of_day",
    "crowd_level",
    "data_quality_flag",
    "top_mentioned_area",
    "top_mentioned_season",
    "top_mentioned_time_of_day",
]

NUMERIC_FEATURES = [
    "month",
    "temperature_avg",
    "precipitation",
    "snowfall",
    "wind_speed",
    "recreation_visits",
    "search_result_count",
    "official_source_count",
    "area_context_count",
    "season_context_count",
    "time_context_count",
    "avg_serp_confidence_score",
    "has_official_context",
]

FEATURE_COLUMNS = CATEGORICAL_FEATURES + NUMERIC_FEATURES


def make_likelihood_target(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby(["park_name", "common_name", "season", "time_of_day"], dropna=False)
        .size()
        .reset_index(name="historical_frequency")
    )
    q1 = grouped["historical_frequency"].quantile(1 / 3)
    q2 = grouped["historical_frequency"].quantile(2 / 3)

    def label(value: int) -> str:
        if value <= q1:
            return "low"
        if value <= q2:
            return "medium"
        return "high"

    grouped["sighting_likelihood_category"] = grouped["historical_frequency"].map(label)
    return df.merge(
        grouped[
            [
                "park_name",
                "common_name",
                "season",
                "time_of_day",
                "historical_frequency",
                "sighting_likelihood_category",
            ]
        ],
        on=["park_name", "common_name", "season", "time_of_day"],
        how="left",
    )


def load_model(path: Path = MODEL_PATH):
    if not path.exists():
        raise FileNotFoundError("Model file missing. Run `python models/train_model.py`.")
    return joblib.load(path)


def save_metrics(metrics: dict, path: Path = METRICS_PATH) -> None:
    path.write_text(json.dumps(metrics, indent=2))
