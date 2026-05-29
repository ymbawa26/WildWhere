import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[2]))
from analysis.wildlife_metrics import data_quality_summary, load_features, missing_value_summary
from app.components.charts import bar_chart
from app.components.layout import configure_page, page_header


configure_page("WildWhere AI | Data Transparency")
page_header(
    "Data Transparency",
    "A clear view of sources, quality flags, missing values, and why reported observations should be interpreted carefully.",
)

df = load_features()
enriched_path = Path(__file__).resolve().parents[2] / "data" / "processed" / "wildlife_features_enriched.csv"

st.subheader("Source List")
st.dataframe(
    pd.DataFrame(
        [
            {"source": "GBIF", "note": "Reported occurrence records collected near parks with bounding boxes."},
            {"source": "NPSpecies", "note": "Official species reference context."},
            {"source": "NPS Stats", "note": "Monthly recreation visitation by park."},
            {"source": "NOAA NCEI", "note": "Daily weather from representative nearby stations."},
        ]
    ),
    use_container_width=True,
)

quality = data_quality_summary(df)
st.plotly_chart(bar_chart(quality, "data_quality_flag", "record_count", "Data Quality Flag Distribution", color="data_quality_flag"), use_container_width=True)

st.subheader("Join Success")
st.write(
    {
        "weather_join_rate": f"{df['weather_joined'].astype(bool).mean():.1%}",
        "visitation_join_rate": f"{df['visitation_joined'].astype(bool).mean():.1%}",
    }
)

st.subheader("Missing Value Summary")
st.dataframe(missing_value_summary(df), use_container_width=True)

st.warning(
    "Reported sightings do not equal confirmed wildlife presence, true population density, or exact wildlife location. "
    "Bounding-box records may include areas outside official park boundaries."
)

st.subheader("SerpApi Public Context Layer")
if enriched_path.exists():
    enriched = pd.read_csv(enriched_path)
    st.write(
        {
            "enriched_rows": len(enriched),
            "total_search_results_joined": int(enriched.get("search_result_count", pd.Series([0])).sum()),
            "official_context_rows": int(enriched.get("has_official_context", pd.Series([False])).astype(bool).sum()),
        }
    )
else:
    st.write("SerpApi enrichment has not been run yet.")
st.info(
    "SerpApi context captures public search mentions such as areas, seasons, and source types. "
    "It is supplemental context, not scientific occurrence evidence."
)
