import re


KNOWN_AREAS = [
    "Lamar Valley",
    "Hayden Valley",
    "Mammoth Hot Springs",
    "Jenny Lake",
    "Oxbow Bend",
    "Logan Pass",
    "Many Glacier",
    "Hurricane Ridge",
    "Paradise",
    "Sunrise",
    "Nisqually",
    "Hoh Rainforest",
    "Old Faithful",
    "Yellowstone Lake",
    "Grand Prismatic",
    "Moraine Park",
    "Going-to-the-Sun Road",
    "Lake McDonald",
    "Sol Duc",
    "Kalaloch",
]

SEASONS = ["spring", "summer", "fall", "autumn", "winter"]
TIMES_OF_DAY = ["early morning", "morning", "afternoon", "evening", "night", "dawn", "dusk"]


def _find_first(text: str, values: list[str]) -> str | None:
    text = text or ""
    for value in values:
        pattern = rf"\b{re.escape(value)}s?\b" if " " not in value else rf"\b{re.escape(value)}\b"
        if re.search(pattern, text, flags=re.IGNORECASE):
            return "fall" if value.lower() == "autumn" else value
    return None


def extract_mentioned_area(text: str) -> str | None:
    return _find_first(text, KNOWN_AREAS)


def extract_mentioned_season(text: str) -> str | None:
    return _find_first(text, SEASONS)


def extract_mentioned_time_of_day(text: str) -> str | None:
    return _find_first(text, TIMES_OF_DAY)
