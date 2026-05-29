import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.settings import PROCESSED_DATA_DIR
from models.predict import predict_sighting_likelihood
from validation.species_eligibility import load_eligibility


GRID_PATH = PROCESSED_DATA_DIR / "valid_prediction_grid.csv"
SEASONS = ["winter", "spring", "summer", "fall"]
TIMES_OF_DAY = ["unknown", "early_morning", "morning", "afternoon", "evening", "night"]


def generate_valid_prediction_grid() -> pd.DataFrame:
    eligibility = load_eligibility()
    eligible = eligibility[eligibility["is_documented_in_park"].astype(bool)].copy()
    rows = []
    for _, row in eligible.iterrows():
        for season in SEASONS:
            for time_of_day in TIMES_OF_DAY:
                result = predict_sighting_likelihood(
                    {
                        "park_name": row["park_name"],
                        "common_name": row["common_name"],
                        "season": season,
                        "time_of_day": time_of_day,
                    }
                )
                rows.append(
                    {
                        "park_name": row["park_name"],
                        "common_name": row["common_name"],
                        "season": season,
                        "time_of_day": time_of_day,
                        "likelihood_category": result["likelihood_category"],
                        "confidence": result["confidence"],
                        "eligibility_status": "eligible",
                        "record_count": result.get("record_count", 0),
                    }
                )
    df = pd.DataFrame(rows)
    df.to_csv(GRID_PATH, index=False)
    print(f"Wrote {len(df)} valid prediction grid rows to {GRID_PATH}")
    return df


if __name__ == "__main__":
    generate_valid_prediction_grid()
