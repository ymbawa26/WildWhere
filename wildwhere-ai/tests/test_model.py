from pathlib import Path

from models.model_utils import METRICS_PATH, MODEL_PATH
from models.predict import predict_sighting_likelihood
from models.train_model import train_model


def test_model_trains_and_creates_files():
    metrics = train_model()
    assert MODEL_PATH.exists()
    assert METRICS_PATH.exists()
    assert "accuracy" in metrics


def test_predict_returns_expected_keys():
    if not MODEL_PATH.exists():
        train_model()
    result = predict_sighting_likelihood({"park_name": "Yellowstone National Park", "common_name": "Bison"})
    assert {"predicted_category", "confidence", "probabilities", "feature_summary", "disclaimer"}.issubset(result)
    assert result["predicted_category"] in {"low", "medium", "high"}
    assert "confirmed wildlife presence" in result["disclaimer"].lower()


def test_missing_optional_fields_do_not_crash_prediction():
    if not MODEL_PATH.exists():
        train_model()
    result = predict_sighting_likelihood({"common_name": "Moose"})
    assert result["predicted_category"] in {"low", "medium", "high"}
