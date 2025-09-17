import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "sightings.csv")
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(BASE_DIR, "models", "wildlife_model.joblib"))

# Features
CATEGORICAL_COLS = ["park", "time_of_day", "region", "weather"]
NUMERIC_COLS = ["month", "temp_c"]
TARGET_COL = "species"


