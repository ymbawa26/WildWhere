from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.settings import PROCESSED_FILES, TARGET_PARKS, TARGET_SPECIES
from models.model_utils import FEATURE_COLUMNS, load_model
from validation.species_eligibility import is_species_eligible


DEFAULT_INPUT = {
    "park_name": "Yellowstone National Park",
    "common_name": "Bison",
    "season": "summer",
    "time_of_day": "unknown",
    "month": 7,
    "temperature_avg": None,
    "precipitation": None,
    "snowfall": None,
    "wind_speed": None,
    "recreation_visits": None,
    "crowd_level": "unknown",
    "data_quality_flag": "bounding_box_only",
    "search_result_count": 0,
    "official_source_count": 0,
    "area_context_count": 0,
    "season_context_count": 0,
    "time_context_count": 0,
    "avg_serp_confidence_score": 0.0,
    "has_official_context": False,
    "top_mentioned_area": "unknown",
    "top_mentioned_season": "unknown",
    "top_mentioned_time_of_day": "unknown",
}


def _blocked_result(category: str, message: str, row: dict, model_used: bool = False) -> dict:
    return {
        "likelihood_category": category,
        "predicted_category": category,
        "estimated_reported_sighting_likelihood": category,
        "probability": 0,
        "confidence": 0,
        "probabilities": {},
        "message": message,
        "model_used": model_used,
        "feature_summary": {column: row.get(column) for column in FEATURE_COLUMNS},
        "disclaimer": "Outputs reflect historical public records and source coverage. They do not represent confirmed wildlife presence or real-time tracking.",
    }


def _historical_record_count(park_name: str, common_name: str) -> int:
    source_path = (
        PROCESSED_FILES["wildlife_features_enriched"]
        if PROCESSED_FILES["wildlife_features_enriched"].exists()
        else PROCESSED_FILES["wildlife_features"]
    )
    df = pd.read_csv(source_path, usecols=["park_name", "common_name"])
    return int(((df["park_name"] == park_name) & (df["common_name"] == common_name)).sum())


def predict_sighting_likelihood(input_dict: dict) -> dict:
    row = DEFAULT_INPUT | dict(input_dict)
    known_parks = {park["park_name"] for park in TARGET_PARKS}
    known_species = {species["common_name"] for species in TARGET_SPECIES}
    if row["park_name"] not in known_parks:
        return _blocked_result("Not supported", "Selected park is not part of the project reference data.", row)
    if row["common_name"] not in known_species:
        return _blocked_result("Not supported", "Selected species is not part of the project reference data.", row)

    eligibility = is_species_eligible(row["park_name"], row["common_name"])
    if not eligibility.get("is_documented_in_park", False):
        return _blocked_result(
            "Not supported",
            "This species is not documented for the selected park in the project's reference data.",
            row,
        )

    record_count = _historical_record_count(row["park_name"], row["common_name"])
    if record_count < 10:
        result = _blocked_result(
            "Insufficient data",
            "Fewer than 10 historical records exist for this park/species combination in the processed dataset.",
            row,
        )
        result["record_count"] = record_count
        return result

    model = load_model()
    frame = pd.DataFrame([{column: row.get(column) for column in FEATURE_COLUMNS}])
    prediction = model.predict(frame)[0]
    probabilities = model.predict_proba(frame)[0]
    classes = list(model.classes_)
    probability_map = {label: float(probabilities[index]) for index, label in enumerate(classes)}
    confidence = probability_map[prediction]
    return {
        "likelihood_category": prediction,
        "predicted_category": prediction,
        "estimated_reported_sighting_likelihood": prediction,
        "probability": confidence,
        "confidence": confidence,
        "probabilities": probability_map,
        "message": "Estimated reported-observation likelihood based on eligible historical records and available public context.",
        "model_used": True,
        "record_count": record_count,
        "feature_summary": {column: row.get(column) for column in FEATURE_COLUMNS},
        "disclaimer": "Outputs reflect historical public records and source coverage. They do not represent confirmed wildlife presence or real-time tracking.",
    }


if __name__ == "__main__":
    print(predict_sighting_likelihood(DEFAULT_INPUT))
