from pathlib import Path

import pandas as pd

from models.generate_prediction_grid import GRID_PATH, generate_valid_prediction_grid
from models.predict import predict_sighting_likelihood


def test_invalid_pair_never_returns_positive_probability():
    result = predict_sighting_likelihood(
        {"park_name": "Mount Rainier National Park", "common_name": "Bison"}
    )
    assert result["likelihood_category"] == "Not supported"
    assert result["probability"] == 0
    assert result["model_used"] is False


def test_sparse_pair_returns_insufficient_data():
    result = predict_sighting_likelihood(
        {"park_name": "Grand Teton National Park", "common_name": "Mountain Goat"}
    )
    assert result["likelihood_category"] == "Insufficient data"
    assert result["probability"] == 0
    assert result["model_used"] is False
    assert result["record_count"] < 10


def test_eligible_pair_can_return_model_category():
    result = predict_sighting_likelihood(
        {
            "park_name": "Yellowstone National Park",
            "common_name": "Bison",
            "season": "summer",
        }
    )
    assert result["likelihood_category"] in {"low", "medium", "high"}
    assert result["model_used"] is True
    assert result["probability"] > 0


def test_prediction_copy_avoids_unsafe_language():
    paths = [
        Path("models/predict.py"),
        Path("app/pages/03_Prediction_Tool.py"),
        Path("public/index.html"),
    ]
    text = "\n".join(path.read_text().lower() for path in paths)
    forbidden = [
        "guaranteed",
        "chance of seeing",
        "probability of seeing",
        "you might see",
        "you will see",
        "animal location",
    ]
    for phrase in forbidden:
        assert phrase not in text


def test_public_preview_uses_valid_prediction_grid_not_fake_estimator():
    html = Path("public/index.html").read_text()
    assert "valid_prediction_grid.csv" in html
    assert "function predict" not in html
    assert "Bison in Mount Rainier National Park returns <strong>Not supported</strong>" in html


def test_valid_prediction_grid_contains_only_eligible_rows():
    if not GRID_PATH.exists():
        generate_valid_prediction_grid()
    grid = pd.read_csv(GRID_PATH)
    assert not grid.empty
    assert set(grid["eligibility_status"]) == {"eligible"}
    invalid = grid[
        (grid["park_name"] == "Mount Rainier National Park")
        & (grid["common_name"] == "Bison")
    ]
    assert invalid.empty
