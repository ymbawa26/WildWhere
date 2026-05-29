import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.settings import PROCESSED_FILES
from enrichment.run_serp_enrichment import ENRICHED_FEATURES_PATH, RAW_SEARCH_PATH
from enrichment.serpapi_client import SERPAPI_RESULT_COLUMNS, get_serpapi_key


def validate_serp_data() -> dict:
    has_key = bool(get_serpapi_key())
    if not RAW_SEARCH_PATH.exists():
        raise FileNotFoundError("Missing serpapi_wildlife_search_results.csv. Run `python enrichment/run_serp_enrichment.py`.")
    raw = pd.read_csv(RAW_SEARCH_PATH)
    missing = sorted(set(SERPAPI_RESULT_COLUMNS) - set(raw.columns))
    if missing:
        raise ValueError(f"SerpApi raw file is missing columns: {missing}")

    failures = []
    if has_key and raw.empty:
        failures.append("SERPAPI_API_KEY exists but raw SerpApi results are empty.")
    if not raw.empty:
        if raw["query"].isna().any():
            failures.append("query contains null values.")
        if raw["park_name"].isna().any() or raw["species_common_name"].isna().any():
            failures.append("park/species fields contain null values.")
        if raw["link"].isna().any():
            failures.append("link contains null values.")
        if raw["source_domain"].isna().any():
            failures.append("source_domain contains null values.")
        scores = pd.to_numeric(raw["confidence_score"], errors="coerce")
        if scores.isna().any():
            failures.append("confidence_score must be numeric.")
        if not scores.between(-2, 10).all():
            failures.append("confidence_score outside expected -2 to 10 range.")
        if raw["date_retrieved"].isna().any():
            failures.append("date_retrieved contains null values.")

    if not ENRICHED_FEATURES_PATH.exists():
        raise FileNotFoundError("Missing wildlife_features_enriched.csv. Run `python enrichment/run_serp_enrichment.py`.")
    enriched = pd.read_csv(ENRICHED_FEATURES_PATH)
    required_enriched = {
        "search_result_count",
        "official_source_count",
        "area_context_count",
        "season_context_count",
        "time_context_count",
        "avg_serp_confidence_score",
        "top_mentioned_area",
        "top_mentioned_season",
        "top_mentioned_time_of_day",
        "has_official_context",
        "has_recent_context",
    }
    missing_enriched = sorted(required_enriched - set(enriched.columns))
    if missing_enriched:
        failures.append(f"enriched features missing columns: {missing_enriched}")
    base_rows = len(pd.read_csv(PROCESSED_FILES["wildlife_features"]))
    if len(enriched) != base_rows:
        failures.append(f"enriched row count {len(enriched)} does not match base wildlife_features row count {base_rows}.")
    if failures:
        raise ValueError("; ".join(failures))
    summary = {
        "has_serpapi_key": has_key,
        "raw_results": int(len(raw)),
        "enriched_rows": int(len(enriched)),
        "status": "PASS",
    }
    print(summary)
    if not has_key:
        print('SERPAPI_API_KEY missing. Add it with: export SERPAPI_API_KEY="your_key_here"')
    return summary


if __name__ == "__main__":
    validate_serp_data()
