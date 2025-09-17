import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier

from src import config

def main():
    # Load dataset
    print(f"Loading data from {config.DATA_PATH} ...")
    df = pd.read_csv(config.DATA_PATH)

    # Split X/y
    X = df[config.CATEGORICAL_COLS + config.NUMERIC_COLS]
    y = df[config.TARGET_COL]

    # Preprocessing
    preproc = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), config.CATEGORICAL_COLS),
            ("num", StandardScaler(), config.NUMERIC_COLS),
        ],
        remainder="drop",
    )

    # Model
    clf = RandomForestClassifier(n_estimators=200, random_state=42)

    pipeline = Pipeline([
        ("preproc", preproc),
        ("clf", clf)
    ])

    # Train
    print("Training model ...")
    pipeline.fit(X, y)

    # Save
    joblib.dump(pipeline, config.MODEL_PATH)
    print(f"Model saved to {config.MODEL_PATH}")

if __name__ == "__main__":
    main()

