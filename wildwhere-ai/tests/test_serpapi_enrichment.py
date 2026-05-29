import pandas as pd

from enrichment.enrich_locations import extract_mentioned_area, extract_mentioned_season, extract_mentioned_time_of_day
from enrichment.enrich_species_context import score_search_context
from enrichment.run_serp_enrichment import ENRICHED_FEATURES_PATH, RAW_SEARCH_PATH, run_serp_enrichment
from enrichment.serpapi_client import SERPAPI_RESULT_COLUMNS
from enrichment.validate_serp_data import validate_serp_data
from enrichment.wildlife_search_queries import generate_search_queries
from models.train_model import load_training_data


def test_serpapi_client_imports():
    import enrichment.serpapi_client  # noqa: F401


def test_query_generation():
    queries = generate_search_queries()
    assert len(queries) == 350
    assert {"query", "park_name", "species_common_name"}.issubset(queries[0])


def test_confidence_score_logic():
    row = {
        "title": "Bison Yellowstone best areas",
        "snippet": "Bison in Yellowstone are often discussed around Lamar Valley in summer mornings.",
        "source_domain": "nps.gov",
        "species_common_name": "Bison",
        "park_name": "Yellowstone National Park",
    }
    assert score_search_context(row) >= 7
    assert extract_mentioned_area(row["snippet"]) == "Lamar Valley"
    assert extract_mentioned_season(row["snippet"]) == "summer"
    assert extract_mentioned_time_of_day(row["snippet"]) == "morning"


def test_serpapi_raw_schema():
    if not RAW_SEARCH_PATH.exists() or not ENRICHED_FEATURES_PATH.exists():
        run_serp_enrichment()
    df = pd.read_csv(RAW_SEARCH_PATH)
    assert set(SERPAPI_RESULT_COLUMNS).issubset(df.columns)
    validate_serp_data()


def test_enriched_features_created():
    if not ENRICHED_FEATURES_PATH.exists():
        run_serp_enrichment()
    df = pd.read_csv(ENRICHED_FEATURES_PATH)
    for column in [
        "search_result_count",
        "official_source_count",
        "area_context_count",
        "season_context_count",
        "time_context_count",
        "avg_serp_confidence_score",
        "top_mentioned_area",
        "has_official_context",
    ]:
        assert column in df.columns
    assert not df.empty


def test_model_uses_enriched_data_if_available():
    if not ENRICHED_FEATURES_PATH.exists():
        run_serp_enrichment()
    df = load_training_data()
    assert "wildlife_features_enriched.csv" in df.attrs.get("training_source", "")


def test_app_displays_serpapi_disclaimer():
    text = open("app/pages/05_Data_Transparency.py").read()
    assert "supplemental context" in text
    assert "not scientific occurrence evidence" in text
