from urllib.parse import urlparse

from enrichment.enrich_locations import (
    extract_mentioned_area,
    extract_mentioned_season,
    extract_mentioned_time_of_day,
)


REPUTABLE_DOMAINS = [
    "nps.gov",
    "nationalgeographic.com",
    "audubon.org",
    "alltrails.com",
    "yellowstone.org",
    "glacier.org",
    "outsideonline.com",
    "earthtrekkers.com",
    "travelwyoming.com",
]


def is_official_nps_domain(domain: str | None) -> bool:
    return bool(domain and domain.endswith("nps.gov"))


def is_reputable_context_domain(domain: str | None) -> bool:
    return bool(domain and any(domain.endswith(value) for value in REPUTABLE_DOMAINS))


def score_search_context(row: dict) -> int:
    title = str(row.get("title") or "")
    snippet = str(row.get("snippet") or "")
    domain = row.get("source_domain")
    species = str(row.get("species_common_name") or "")
    park = str(row.get("park_name") or "").replace(" National Park", "")
    combined = f"{title} {snippet}"
    score = 0
    if is_official_nps_domain(domain):
        score += 3
    elif is_reputable_context_domain(domain):
        score += 2
    if species.lower() in title.lower() and park.lower() in title.lower():
        score += 2
    if species.lower() in snippet.lower() and park.lower() in snippet.lower():
        score += 1
    if extract_mentioned_area(combined):
        score += 1
    if extract_mentioned_season(combined) or extract_mentioned_time_of_day(combined):
        score += 1
    generic_terms = ["images", "clipart", "wallpaper", "definition"]
    if any(term in combined.lower() for term in generic_terms):
        score -= 2
    return score


def enrich_result(row: dict) -> dict:
    text = f"{row.get('title') or ''} {row.get('snippet') or ''}"
    row["mentioned_area"] = extract_mentioned_area(text)
    row["mentioned_season"] = extract_mentioned_season(text)
    row["mentioned_time_of_day"] = extract_mentioned_time_of_day(text)
    row["confidence_score"] = score_search_context(row)
    return row
