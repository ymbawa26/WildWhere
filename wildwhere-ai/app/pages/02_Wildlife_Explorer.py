import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[2]))
from analysis.wildlife_metrics import load_features, sightings_by_season
from app.components.charts import bar_chart, line_chart
from app.components.layout import caveat, configure_page, page_header


configure_page("WildWhere AI | Wildlife Explorer")
page_header(
    "Wildlife Explorer",
    "Filter reported observation records by park, species, season, source, and quality flag. Map points are reported coordinates and may include bounding-box records near parks.",
)

df = load_features()
enriched_path = Path(__file__).resolve().parents[2] / "data" / "processed" / "wildlife_features_enriched.csv"
if enriched_path.exists():
    import pandas as pd

    df = pd.read_csv(enriched_path, parse_dates=["event_date"])
with st.sidebar:
    parks = st.multiselect("Park", sorted(df["park_name"].unique()), default=sorted(df["park_name"].unique()))
    species = st.multiselect("Species", sorted(df["common_name"].unique()), default=sorted(df["common_name"].unique()))
    seasons = st.multiselect("Season", sorted(df["season"].unique()), default=sorted(df["season"].unique()))
    times = st.multiselect("Time of day", sorted(df["time_of_day"].unique()), default=sorted(df["time_of_day"].unique()))
    flags = st.multiselect("Data quality flag", sorted(df["data_quality_flag"].unique()), default=sorted(df["data_quality_flag"].unique()))
    if "top_mentioned_area" in df.columns:
        areas = sorted(df["top_mentioned_area"].dropna().unique())
        selected_areas = st.multiselect("Top mentioned area", areas, default=areas)
        official_options = sorted(df["has_official_context"].dropna().unique())
        selected_official = st.multiselect("Has official context", official_options, default=official_options)
        min_confidence = st.slider("Minimum search-context confidence", 0.0, float(df["avg_serp_confidence_score"].max() or 0), 0.0)
    else:
        selected_areas = []
        selected_official = []
        min_confidence = 0.0

filtered = df[
    df["park_name"].isin(parks)
    & df["common_name"].isin(species)
    & df["season"].isin(seasons)
    & df["time_of_day"].isin(times)
    & df["data_quality_flag"].isin(flags)
]
if "top_mentioned_area" in filtered.columns and selected_areas:
    filtered = filtered[
        filtered["top_mentioned_area"].isin(selected_areas)
        & filtered["has_official_context"].isin(selected_official)
        & (filtered["avg_serp_confidence_score"] >= min_confidence)
    ]

caveat()
st.metric("Filtered reported observations", f"{len(filtered):,}")

monthly = filtered.groupby("month").size().reindex(range(1, 13), fill_value=0).reset_index(name="sighting_count")
left, right = st.columns(2)
with left:
    st.plotly_chart(line_chart(monthly, "month", "sighting_count", "Reported Sightings By Month"), use_container_width=True)
with right:
    st.plotly_chart(bar_chart(sightings_by_season(filtered), "season", "sighting_count", "Reported Sightings By Season"), use_container_width=True)

if not filtered.empty:
    st.map(filtered.rename(columns={"decimal_latitude": "lat", "decimal_longitude": "lon"})[["lat", "lon"]])

st.subheader("Filtered Records")
st.dataframe(
    filtered[
        [
            "park_name",
            "common_name",
            "event_date",
            "season",
            "time_of_day",
            "decimal_latitude",
            "decimal_longitude",
            "coordinate_uncertainty",
            "data_quality_flag",
            *([column for column in ["top_mentioned_area", "avg_serp_confidence_score", "has_official_context"] if column in filtered.columns]),
            "source",
        ]
    ].head(1000),
    use_container_width=True,
)
