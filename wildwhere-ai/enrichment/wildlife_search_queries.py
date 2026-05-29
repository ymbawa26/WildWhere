import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.settings import TARGET_PARKS, TARGET_SPECIES


QUERY_TEMPLATES = [
    "{species} sightings {park} best area",
    "{species} {park} trail wildlife viewing",
    "{species} {park} recent sightings",
    "{species} {park} best time of day",
    "{species} {park} seasonal viewing",
    "{park} wildlife viewing {species}",
    "{park} {species} valley trail overlook",
]


def park_display_name(park_name: str) -> str:
    return park_name.replace(" National Park", "")


def generate_search_queries() -> list[dict]:
    queries = []
    for park in TARGET_PARKS:
        park_name = park["park_name"]
        short_park = park_display_name(park_name)
        for species in TARGET_SPECIES:
            common_name = species["common_name"]
            for template in QUERY_TEMPLATES:
                query = template.format(species=common_name, park=short_park)
                queries.append(
                    {
                        "query": query,
                        "park_name": park_name,
                        "species_common_name": common_name,
                    }
                )
    return queries
