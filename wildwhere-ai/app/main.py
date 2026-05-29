import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from ai.insight_generator import generate_data_quality_note
from analysis.wildlife_metrics import (
    date_range,
    load_features,
    sightings_by_park,
    sightings_by_season,
    sightings_by_species,
)
from app.components.cards import metric_card
from app.components.charts import bar_chart
from app.components.layout import caveat, configure_page, page_header


configure_page("WildWhere AI | Overview")
page_header(
    "Wildlife Intelligence From Public Data",
    "A portfolio-grade analytics project using real biodiversity, park, weather, and visitation datasets to study historical reported wildlife observation patterns.",
)

df = load_features()
start_date, end_date = date_range(df)

cols = st.columns(4)
with cols[0]:
    metric_card("Processed sighting records", f"{len(df):,}", "Cleaned GBIF near-park records")
with cols[1]:
    metric_card("Parks covered", f"{df['park_name'].nunique()}", "Target U.S. national parks")
with cols[2]:
    metric_card("Target species", f"{df['common_name'].nunique()}", "Portfolio species set")
with cols[3]:
    metric_card("Date range", f"{start_date.date()} to {end_date.date()}", "Reported observation dates")

caveat()

left, right = st.columns(2)
with left:
    st.plotly_chart(bar_chart(sightings_by_species(df).head(10), "common_name", "sighting_count", "Top Reported Species"), use_container_width=True)
with right:
    st.plotly_chart(bar_chart(sightings_by_park(df), "park_name", "sighting_count", "Reported Sightings By Park"), use_container_width=True)

st.plotly_chart(bar_chart(sightings_by_season(df), "season", "sighting_count", "Seasonal Reported Observation Pattern"), use_container_width=True)

st.subheader("Data Quality Note")
st.write(generate_data_quality_note())

st.subheader("Public Context Enrichment")
st.write(
    "Step 3.5 optionally enriches the model with SerpApi search-derived context such as named viewing areas, "
    "seasonal mentions, and official-source counts. This context supports interpretation but does not replace GBIF, NPS, NOAA, or visitation data."
)

st.subheader("Data Sources")
st.dataframe(
    pd.DataFrame(
        [
            {"source": "GBIF", "role": "Near-park wildlife occurrence records"},
            {"source": "NPSpecies", "role": "Official park species reference context"},
            {"source": "NPS Visitor Use Statistics", "role": "Monthly recreation visitation"},
            {"source": "NOAA NCEI", "role": "Daily weather near target parks"},
        ]
    ),
    use_container_width=True,
)
