import sys
from pathlib import Path

import streamlit as st
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[2]))
from ai.insight_generator import generate_prediction_explanation
from analysis.wildlife_metrics import load_features
from app.components.layout import caveat, configure_page, page_header
from models.predict import predict_sighting_likelihood
from validation.species_eligibility import load_eligibility


configure_page("WildWhere AI | Prediction Tool")
page_header(
    "Estimated Reported-Observation Likelihood",
    "Evaluate historical reported-observation patterns for park/species combinations documented in the project reference data.",
)

df = load_features()
enriched_path = Path(__file__).resolve().parents[2] / "data" / "processed" / "wildlife_features_enriched.csv"
enriched_df = pd.read_csv(enriched_path) if enriched_path.exists() else df.copy()
eligibility = load_eligibility()
left, right = st.columns(2)
with left:
    park = st.selectbox("Park", sorted(df["park_name"].unique()))
    eligible_species = sorted(
        eligibility[
            (eligibility["park_name"] == park)
            & (eligibility["is_documented_in_park"].astype(bool))
        ]["common_name"].unique()
    )
    if eligible_species:
        species = st.selectbox("Species", eligible_species)
        st.caption("Species options are filtered using official park-species reference data where available.")
    else:
        species = None
        st.warning("No eligible target species are documented for this park in the current reference data.")
    season = st.selectbox("Season", ["winter", "spring", "summer", "fall"])
    time_of_day = st.selectbox("Time of day", ["unknown", "early_morning", "morning", "afternoon", "evening", "night"])
    crowd_level = st.selectbox("Crowd level", ["unknown", "low", "medium", "high"])
with right:
    month = st.slider("Month", 1, 12, 7)
    temperature_avg = st.number_input("Average temperature (C)", value=10.0)
    precipitation = st.number_input("Precipitation (mm)", value=0.0, min_value=0.0)
    snowfall = st.number_input("Snowfall (mm)", value=0.0, min_value=0.0)
    wind_speed = st.number_input("Wind speed", value=0.0, min_value=0.0)
    recreation_visits = st.number_input("Monthly recreation visits", value=100000.0, min_value=0.0)

if st.button("Evaluate reported-observation pattern", type="primary", disabled=species is None):
    context_rows = enriched_df[(enriched_df["park_name"] == park) & (enriched_df["common_name"] == species)]
    context = context_rows.iloc[0].to_dict() if not context_rows.empty else {}
    result = predict_sighting_likelihood(
        {
            "park_name": park,
            "common_name": species,
            "season": season,
            "time_of_day": time_of_day,
            "month": month,
            "temperature_avg": temperature_avg,
            "precipitation": precipitation,
            "snowfall": snowfall,
            "wind_speed": wind_speed,
            "recreation_visits": recreation_visits,
            "crowd_level": crowd_level,
            "data_quality_flag": "bounding_box_only",
            "search_result_count": context.get("search_result_count", 0),
            "official_source_count": context.get("official_source_count", 0),
            "area_context_count": context.get("area_context_count", 0),
            "season_context_count": context.get("season_context_count", 0),
            "time_context_count": context.get("time_context_count", 0),
            "avg_serp_confidence_score": context.get("avg_serp_confidence_score", 0),
            "has_official_context": context.get("has_official_context", False),
            "top_mentioned_area": context.get("top_mentioned_area", "unknown"),
            "top_mentioned_season": context.get("top_mentioned_season", "unknown"),
            "top_mentioned_time_of_day": context.get("top_mentioned_time_of_day", "unknown"),
        }
    )
    if not result["model_used"]:
        st.warning(result["likelihood_category"])
        st.write(result["message"])
    else:
        st.metric("Estimated reported-observation likelihood", result["likelihood_category"].title(), f"{result['confidence']:.1%} model confidence")
        st.write(generate_prediction_explanation(result))
        st.subheader("Public Context Signals")
        st.write(
            {
                "top_mentioned_area": result["feature_summary"].get("top_mentioned_area", "unknown"),
                "search_context_confidence": result["feature_summary"].get("avg_serp_confidence_score", 0),
                "official_source_count": result["feature_summary"].get("official_source_count", 0),
                "search_result_count": result["feature_summary"].get("search_result_count", 0),
            }
        )
        st.json(result["probabilities"])

caveat()
