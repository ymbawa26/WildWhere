# app.py
from __future__ import annotations

import os
import json
from typing import List, Optional, Tuple

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pydantic import BaseModel, Field, ValidationError, field_validator
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import joblib

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier

# -----------------------------
# Environment & App Setup
# -----------------------------
load_dotenv()
MODEL_PATH = os.getenv("MODEL_PATH", "models/wildlife_model.joblib")

app = Flask(__name__, static_folder="web", static_url_path="")
CORS(app)


# -----------------------------
# Request / Response Schemas
# (kept local for now; we can refactor to src/data_schema.py later)
# -----------------------------
class PredictRequest(BaseModel):
    park: str = Field(..., description="Name of the national park, e.g., 'Yellowstone'")
    month: int = Field(..., ge=1, le=12, description="Month as integer 1-12")
    time_of_day: str = Field(..., description="One of: dawn, day, dusk, night")
    region: Optional[str] = Field(None, description="Area/region/quadrant in the park (optional)")
    weather: Optional[str] = Field(None, description="Weather summary, e.g., 'sunny', 'cloudy' (optional)")
    temp_c: Optional[float] = Field(None, description="Temperature in Celsius (optional)")
    top_n: int = Field(5, ge=1, le=20, description="How many top species to return")

    @field_validator("time_of_day")
    @classmethod
    def normalize_tod(cls, v: str) -> str:
        v_norm = v.strip().lower()
        allowed = {"dawn", "day", "dusk", "night"}
        if v_norm not in allowed:
            raise ValueError(f"time_of_day must be one of {sorted(allowed)}")
        return v_norm

    @field_validator("park")
    @classmethod
    def strip_park(cls, v: str) -> str:
        return v.strip()


class SpeciesProb(BaseModel):
    species: str
    probability: float


class PredictResponse(BaseModel):
    park: str
    month: int
    time_of_day: str
    results: List[SpeciesProb]


# -----------------------------
# Model Loading / Fallback
# -----------------------------
_model_pipeline: Optional[Pipeline] = None
_feature_cols_cat = ["park", "time_of_day", "region", "weather"]
_feature_cols_num = ["month", "temp_c"]


def _build_fallback_model() -> Pipeline:
    """
    Builds a tiny synthetic model so the API works before you train on real data.
    You should replace this by running `python -m src.train` to produce models/wildlife_model.joblib.
    """
    rng = np.random.default_rng(42)

    # Synthetic "dataset"
    parks = ["Yellowstone", "Glacier", "Grand Teton", "Olympic", "Mount Rainier"]
    times = ["dawn", "day", "dusk", "night"]
    regions = ["north", "south", "east", "west"]
    weathers = ["sunny", "cloudy", "rainy"]

    species = [
        "bison", "elk", "grizzly_bear", "black_bear", "wolf",
        "moose", "mountain_goat", "bighorn_sheep", "otter", "eagle"
    ]

    rows = []
    for _ in range(1000):
        park = rng.choice(parks)
        tod = rng.choice(times)
        region = rng.choice(regions)
        weather = rng.choice(weathers)
        month = int(rng.integers(1, 13))
        temp_c = float(rng.normal(10 + (month - 6) * 2, 5))

        # crude heuristic for species label
        if park == "Yellowstone" and tod in {"dawn", "dusk"}:
            y = rng.choice(["bison", "wolf", "elk"], p=[0.5, 0.2, 0.3])
        elif park == "Glacier" and tod in {"day", "dusk"}:
            y = rng.choice(["grizzly_bear", "mountain_goat", "moose"], p=[0.35, 0.4, 0.25])
        elif park == "Grand Teton":
            y = rng.choice(["elk", "moose", "bison"], p=[0.5, 0.3, 0.2])
        elif park == "Olympic":
            y = rng.choice(["black_bear", "otter", "eagle"], p=[0.4, 0.35, 0.25])
        else:
            y = rng.choice(species)

        rows.append(
            {
                "park": park,
                "time_of_day": tod,
                "region": region,
                "weather": weather,
                "month": month,
                "temp_c": temp_c,
                "species": y,
            }
        )

    df = pd.DataFrame(rows)

    preproc = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), _feature_cols_cat),
            ("num", StandardScaler(), _feature_cols_num),
        ],
        remainder="drop",
    )

    clf = RandomForestClassifier(
        n_estimators=200, random_state=1337, class_weight=None
    )

    pipe = Pipeline(
        steps=[
            ("preprocess", preproc),
            ("clf", clf),
        ]
    )

    X = df[_feature_cols_cat + _feature_cols_num]
    y = df["species"]
    pipe.fit(X, y)
    return pipe


def load_model() -> Tuple[Pipeline, bool]:
    """
    Returns (pipeline, is_fallback)
    """
    global _model_pipeline
    if _model_pipeline is not None:
        return _model_pipeline, False

    if os.path.exists(MODEL_PATH):
        try:
            _model_pipeline = joblib.load(MODEL_PATH)
            app.logger.info(f"Loaded model from {MODEL_PATH}")
            return _model_pipeline, False
        except Exception as e:
            app.logger.warning(f"Failed to load {MODEL_PATH}: {e}. Using fallback model.")

    _model_pipeline = _build_fallback_model()
    app.logger.info("Initialized fallback synthetic model.")
    return _model_pipeline, True


# -----------------------------
# Helpers
# -----------------------------
def _to_dataframe(req: PredictRequest) -> pd.DataFrame:
    """
    Convert validated request into a single-row DataFrame
    matching the model's expected columns.
    """
    row = {
        "park": req.park,
        "time_of_day": req.time_of_day,
        "region": req.region or "unknown",
        "weather": req.weather or "unknown",
        "month": req.month,
        "temp_c": req.temp_c if req.temp_c is not None else float("nan"),
    }
    return pd.DataFrame([row], columns=_feature_cols_cat + _feature_cols_num)


def _top_n_from_proba(model: Pipeline, X: pd.DataFrame, top_n: int) -> List[SpeciesProb]:
    proba = model.predict_proba(X)[0]
    classes = model.named_steps["clf"].classes_
    order = np.argsort(proba)[::-1][:top_n]
    return [SpeciesProb(species=str(classes[i]), probability=float(proba[i])) for i in order]


# -----------------------------
# Routes
# -----------------------------
def health_payload():
    _, is_fallback = load_model()
    return {
        "status": "ok",
        "model_path": MODEL_PATH if os.path.exists(MODEL_PATH) else None,
        "using_fallback": bool(is_fallback),
    }


@app.get("/health")
def health():
    return jsonify(health_payload())


@app.get("/api/health")
def health_alias():
    return jsonify(health_payload())


@app.post("/predict")
def predict():
    """
    Request JSON (example):
    {
      "park": "Yellowstone",
      "month": 7,
      "time_of_day": "dawn",
      "region": "north",
      "weather": "sunny",
      "temp_c": 12.5,
      "top_n": 5
    }
    """
    try:
        payload = request.get_json(force=True, silent=False)
        req = PredictRequest(**payload)
    except (ValidationError, TypeError, json.JSONDecodeError) as e:
        return jsonify({"error": "Invalid request body", "details": str(e)}), 400

    model, _ = load_model()
    X = _to_dataframe(req)

    try:
        results = _top_n_from_proba(model, X, req.top_n)
        resp = PredictResponse(
            park=req.park,
            month=req.month,
            time_of_day=req.time_of_day,
            results=results,
        )
        return jsonify(json.loads(resp.model_dump_json()))
    except Exception as e:
        app.logger.exception("Prediction failed")
        return jsonify({"error": "Prediction failed", "details": str(e)}), 500


@app.post("/api/predict")
def predict_alias():
    return predict()


@app.get("/api")
def api_root():
    return jsonify(
        {
            "message": "WildWhere 2.0 API",
            "endpoints": {
                "GET /health": "Service status",
                "POST /predict": "Predict top-N likely species for given trip context",
            },
        }
    )


@app.get("/")
def root():
    return send_from_directory(app.static_folder, "index.html")


# -----------------------------
# Entrypoint
# -----------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("DEBUG", "true").lower() in {"1", "true", "yes"}
    app.run(host="0.0.0.0", port=port, debug=debug)
