import hashlib
import os
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests


SERPAPI_ENDPOINT = "https://serpapi.com/search.json"
SERPAPI_RESULT_COLUMNS = [
    "serp_result_id",
    "query",
    "park_name",
    "species_common_name",
    "title",
    "link",
    "snippet",
    "source_domain",
    "position",
    "date_retrieved",
    "result_type",
    "mentioned_area",
    "mentioned_season",
    "mentioned_time_of_day",
    "confidence_score",
]


def load_env_file(path: Path | None = None) -> None:
    env_path = path or Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        if not line.strip() or line.strip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_serpapi_key() -> str | None:
    load_env_file()
    return os.getenv("SERPAPI_API_KEY")


def source_domain(link: str | None) -> str | None:
    if not link or not isinstance(link, str):
        return None
    parsed = urlparse(link)
    return parsed.netloc.replace("www.", "") or None


def stable_result_id(query: str, link: str | None, position: int | None) -> str:
    raw = f"{query}|{link or ''}|{position or ''}"
    return "serp_" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def query_serpapi(query: str, api_key: str, num_results: int = 10) -> dict:
    response = requests.get(
        SERPAPI_ENDPOINT,
        params={
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "num": num_results,
        },
        timeout=45,
    )
    response.raise_for_status()
    return response.json()


def empty_results_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=SERPAPI_RESULT_COLUMNS)


def today_string() -> str:
    return date.today().isoformat()
