import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.settings import PROCESSED_FILES
from models.model_utils import (
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    METRICS_PATH,
    MODEL_PATH,
    NUMERIC_FEATURES,
    make_likelihood_target,
    save_metrics,
)
from validation.species_eligibility import ELIGIBILITY_PATH, build_park_species_eligibility, load_eligibility


def load_training_data() -> pd.DataFrame:
    source_path = (
        PROCESSED_FILES["wildlife_features_enriched"]
        if PROCESSED_FILES["wildlife_features_enriched"].exists()
        else PROCESSED_FILES["wildlife_features"]
    )
    if not source_path.exists():
        raise FileNotFoundError("Missing wildlife_features.csv. Run `python etl/run_pipeline.py`.")
    df = pd.read_csv(source_path)
    for column in FEATURE_COLUMNS:
        if column not in df.columns:
            df[column] = None
    if not ELIGIBILITY_PATH.exists():
        build_park_species_eligibility()
    eligibility = load_eligibility()[["park_name", "common_name", "is_documented_in_park", "confidence_level"]]
    before = len(df)
    df = df.merge(eligibility, on=["park_name", "common_name"], how="left")
    df["is_documented_in_park"] = df["is_documented_in_park"].fillna(False).astype(bool)
    invalid_rows = int((~df["is_documented_in_park"]).sum())
    df = df[df["is_documented_in_park"]].copy()
    bounding_low_confidence = (
        df["data_quality_flag"].eq("bounding_box_only")
        & df["location_filter_method"].eq("bounding_box")
        & ~df["confidence_level"].eq("high")
    )
    removed_bounding_rows = int(bounding_low_confidence.sum())
    df = df[~bounding_low_confidence].copy()
    df = make_likelihood_target(df)
    df.attrs["training_source"] = str(source_path)
    df.attrs["removed_invalid_rows"] = invalid_rows
    df.attrs["removed_bounding_rows"] = removed_bounding_rows
    df.attrs["eligible_combinations"] = int(eligibility["is_documented_in_park"].astype(bool).sum())
    df.attrs["source_rows"] = before
    result = df.dropna(subset=["sighting_likelihood_category"]).copy()
    result.attrs.update(df.attrs)
    return result


def sample_weights(df: pd.DataFrame) -> pd.Series:
    return df["data_quality_flag"].map(
        {
            "high_confidence": 1.0,
            "coordinate_uncertain": 0.5,
            "bounding_box_only": 0.25,
            "missing_time": 0.5,
            "limited_metadata": 0.5,
        }
    ).fillna(0.5)


def build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="constant", fill_value="unknown")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                CATEGORICAL_FEATURES,
            ),
            (
                "numeric",
                Pipeline([("imputer", SimpleImputer(strategy="median"))]),
                NUMERIC_FEATURES,
            ),
        ]
    )
    return Pipeline(
        [
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(n_estimators=160, random_state=42, class_weight="balanced")),
        ]
    )


def train_model() -> dict:
    df = load_training_data()
    x = df[FEATURE_COLUMNS]
    y = df["sighting_likelihood_category"]
    stratify = y if y.value_counts().min() >= 2 else None
    x_train, x_test, y_train, y_test, weights_train, weights_test = train_test_split(
        x,
        y,
        sample_weights(df),
        test_size=0.25,
        random_state=42,
        stratify=stratify,
    )
    model = build_pipeline()
    model.fit(x_train, y_train, classifier__sample_weight=weights_train)
    predictions = model.predict(x_test)
    labels = sorted(y.unique())
    metrics = {
        "model_type": "RandomForestClassifier",
        "target": "estimated_reported_sighting_likelihood",
        "training_source": df.attrs.get("training_source", "unknown"),
        "uses_serpapi_enrichment": "search_result_count" in df.columns and "enriched" in df.attrs.get("training_source", ""),
        "accuracy": float(accuracy_score(y_test, predictions)),
        "classification_report": classification_report(y_test, predictions, output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(y_test, predictions, labels=labels).tolist(),
        "labels": labels,
        "training_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "removed_invalid_rows": int(df.attrs.get("removed_invalid_rows", 0)),
        "removed_bounding_box_low_confidence_rows": int(df.attrs.get("removed_bounding_rows", 0)),
        "eligible_park_species_combinations": int(df.attrs.get("eligible_combinations", 0)),
        "source_rows_before_filtering": int(df.attrs.get("source_rows", len(df))),
        "important_note": "This model estimates reported-observation likelihood from historical records and supplemental public context. It does not predict confirmed wildlife presence.",
    }
    try:
        feature_names = model.named_steps["preprocessor"].get_feature_names_out()
        importances = model.named_steps["classifier"].feature_importances_
        metrics["feature_importance"] = [
            {"feature": feature, "importance": float(importance)}
            for feature, importance in sorted(zip(feature_names, importances), key=lambda item: item[1], reverse=True)[:20]
        ]
    except Exception:
        metrics["feature_importance"] = []

    joblib.dump(model, MODEL_PATH)
    save_metrics(metrics, METRICS_PATH)
    print(f"Saved model to {MODEL_PATH}")
    print(f"Saved metrics to {METRICS_PATH}")
    print(f"Accuracy: {metrics['accuracy']:.3f}")
    return metrics


if __name__ == "__main__":
    train_model()
