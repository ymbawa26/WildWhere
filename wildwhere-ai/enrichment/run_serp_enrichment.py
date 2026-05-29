import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.settings import PROCESSED_FILES, RAW_DATA_DIR, PROCESSED_DATA_DIR
from enrichment.enrich_species_context import enrich_result, is_official_nps_domain
from enrichment.serpapi_client import (
    SERPAPI_RESULT_COLUMNS,
    empty_results_frame,
    get_serpapi_key,
    query_serpapi,
    source_domain,
    stable_result_id,
    today_string,
)
from enrichment.wildlife_search_queries import generate_search_queries


RAW_SEARCH_PATH = RAW_DATA_DIR / "serpapi_wildlife_search_results.csv"
LOCATION_CONTEXT_PATH = RAW_DATA_DIR / "serpapi_location_context.csv"
SPECIES_CONTEXT_PATH = RAW_DATA_DIR / "serpapi_species_context.csv"
ENRICHED_FEATURES_PATH = PROCESSED_DATA_DIR / "wildlife_features_enriched.csv"


def organic_results_to_rows(payload: dict, query_meta: dict) -> list[dict]:
    rows = []
    for result in payload.get("organic_results", []):
        position = result.get("position")
        link = result.get("link")
        row = {
            "serp_result_id": stable_result_id(query_meta["query"], link, position),
            "query": query_meta["query"],
            "park_name": query_meta["park_name"],
            "species_common_name": query_meta["species_common_name"],
            "title": result.get("title"),
            "link": link,
            "snippet": result.get("snippet"),
            "source_domain": source_domain(link),
            "position": position,
            "date_retrieved": today_string(),
            "result_type": "organic",
            "mentioned_area": None,
            "mentioned_season": None,
            "mentioned_time_of_day": None,
            "confidence_score": 0,
        }
        rows.append(enrich_result(row))
    return rows


def write_empty_raw_files() -> None:
    empty_results_frame().to_csv(RAW_SEARCH_PATH, index=False)
    pd.DataFrame(
        columns=[
            "park_name",
            "mentioned_area",
            "result_count",
            "avg_serp_confidence_score",
            "date_retrieved",
        ]
    ).to_csv(LOCATION_CONTEXT_PATH, index=False)
    pd.DataFrame(
        columns=[
            "park_name",
            "species_common_name",
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
            "date_retrieved",
        ]
    ).to_csv(SPECIES_CONTEXT_PATH, index=False)


def aggregate_context(results: pd.DataFrame) -> pd.DataFrame:
    if results.empty:
        return pd.read_csv(SPECIES_CONTEXT_PATH) if SPECIES_CONTEXT_PATH.exists() else pd.DataFrame()

    def top_non_null(series: pd.Series) -> str:
        values = series.dropna()
        if values.empty:
            return "unknown"
        return str(values.value_counts().idxmax())

    grouped = (
        results.groupby(["park_name", "species_common_name"], dropna=False)
        .agg(
            search_result_count=("serp_result_id", "count"),
            official_source_count=("source_domain", lambda s: int(sum(is_official_nps_domain(v) for v in s))),
            area_context_count=("mentioned_area", lambda s: int(s.notna().sum())),
            season_context_count=("mentioned_season", lambda s: int(s.notna().sum())),
            time_context_count=("mentioned_time_of_day", lambda s: int(s.notna().sum())),
            avg_serp_confidence_score=("confidence_score", "mean"),
            top_mentioned_area=("mentioned_area", top_non_null),
            top_mentioned_season=("mentioned_season", top_non_null),
            top_mentioned_time_of_day=("mentioned_time_of_day", top_non_null),
            date_retrieved=("date_retrieved", "max"),
        )
        .reset_index()
    )
    grouped["has_official_context"] = grouped["official_source_count"] > 0
    grouped["has_recent_context"] = results.groupby(["park_name", "species_common_name"])["query"].apply(
        lambda s: s.str.contains("recent", case=False, na=False).any()
    ).values
    return grouped


def create_location_context(results: pd.DataFrame) -> pd.DataFrame:
    if results.empty:
        return pd.DataFrame(columns=["park_name", "mentioned_area", "result_count", "avg_serp_confidence_score", "date_retrieved"])
    return (
        results.dropna(subset=["mentioned_area"])
        .groupby(["park_name", "mentioned_area"], dropna=False)
        .agg(
            result_count=("serp_result_id", "count"),
            avg_serp_confidence_score=("confidence_score", "mean"),
            date_retrieved=("date_retrieved", "max"),
        )
        .reset_index()
    )


def create_enriched_features(context: pd.DataFrame) -> pd.DataFrame:
    features = pd.read_csv(PROCESSED_FILES["wildlife_features"])
    if context.empty:
        enriched = features.copy()
        enriched["search_result_count"] = 0
        enriched["official_source_count"] = 0
        enriched["area_context_count"] = 0
        enriched["season_context_count"] = 0
        enriched["time_context_count"] = 0
        enriched["avg_serp_confidence_score"] = 0.0
        enriched["top_mentioned_area"] = "unknown"
        enriched["top_mentioned_season"] = "unknown"
        enriched["top_mentioned_time_of_day"] = "unknown"
        enriched["has_official_context"] = False
        enriched["has_recent_context"] = False
        return enriched

    enriched = features.merge(
        context,
        left_on=["park_name", "common_name"],
        right_on=["park_name", "species_common_name"],
        how="left",
    ).drop(columns=["species_common_name"], errors="ignore")
    numeric_defaults = {
        "search_result_count": 0,
        "official_source_count": 0,
        "area_context_count": 0,
        "season_context_count": 0,
        "time_context_count": 0,
        "avg_serp_confidence_score": 0.0,
    }
    for column, value in numeric_defaults.items():
        enriched[column] = enriched[column].fillna(value)
    for column in ["top_mentioned_area", "top_mentioned_season", "top_mentioned_time_of_day"]:
        enriched[column] = enriched[column].fillna("unknown")
    for column in ["has_official_context", "has_recent_context"]:
        enriched[column] = enriched[column].fillna(False).astype(bool)
    return enriched


def run_serp_enrichment(force: bool = False, max_queries: int | None = None) -> dict:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    api_key = get_serpapi_key()
    queries = generate_search_queries()
    if max_queries is not None:
        queries = queries[:max_queries]

    if not api_key:
        print("SERPAPI_API_KEY is not set. Skipping live SerpApi collection and writing schema-valid empty context files.")
        write_empty_raw_files()
        context = pd.read_csv(SPECIES_CONTEXT_PATH)
        enriched = create_enriched_features(context)
        enriched.to_csv(ENRICHED_FEATURES_PATH, index=False)
        return {"queries_planned": len(queries), "queries_run": 0, "results_collected": 0, "skipped": True}

    if RAW_SEARCH_PATH.exists() and not force:
        print(f"Using existing {RAW_SEARCH_PATH}. Pass --force to run SerpApi again.")
        results = pd.read_csv(RAW_SEARCH_PATH)
    else:
        rows = []
        for index, query_meta in enumerate(queries, start=1):
            print(f"SerpApi {index}/{len(queries)}: {query_meta['query']}")
            payload = query_serpapi(query_meta["query"], api_key)
            rows.extend(organic_results_to_rows(payload, query_meta))
        results = pd.DataFrame(rows, columns=SERPAPI_RESULT_COLUMNS).drop_duplicates(subset=["serp_result_id"])
        results.to_csv(RAW_SEARCH_PATH, index=False)

    context = aggregate_context(results)
    context.to_csv(SPECIES_CONTEXT_PATH, index=False)
    create_location_context(results).to_csv(LOCATION_CONTEXT_PATH, index=False)
    enriched = create_enriched_features(context)
    enriched.to_csv(ENRICHED_FEATURES_PATH, index=False)
    return {
        "queries_planned": len(queries),
        "queries_run": len(queries),
        "results_collected": int(len(results)),
        "skipped": False,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SerpApi enrichment for WildWhere AI.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing SerpApi raw results.")
    parser.add_argument("--max-queries", type=int, default=None, help="Optional cap for controlled SerpApi usage.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    summary = run_serp_enrichment(force=args.force, max_queries=args.max_queries)
    print(summary)
