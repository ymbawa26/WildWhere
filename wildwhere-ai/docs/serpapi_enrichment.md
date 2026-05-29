# SerpApi Enrichment

Step 3.5 adds an optional SerpApi search-context layer to WildWhere AI.

## Why It Was Added

The original model uses strong structured sources: GBIF, NPSpecies, NOAA, and NPS visitation. Those sources are more appropriate for scientific and analytical grounding, but they do not capture public wildlife-viewing context such as named valleys, overlooks, seasonal advice, or commonly mentioned viewing areas.

SerpApi is used only as supplemental context. It does not replace official or scientific data.

## Required Key

```bash
export SERPAPI_API_KEY="your_key_here"
```

You can also place the key in a local `.env` file:

```text
SERPAPI_API_KEY=your_key_here
```

Do not commit `.env`.

## Queries Used

For each target park and species combination, the enrichment layer generates queries such as:

- `{species} sightings {park} best area`
- `{species} {park} trail wildlife viewing`
- `{species} {park} recent sightings`
- `{species} {park} best time of day`
- `{species} {park} seasonal viewing`
- `{park} wildlife viewing {species}`
- `{park} {species} valley trail overlook`

With 5 parks, 10 species, and 7 templates, the full planned query set contains 350 searches. Use `--max-queries` for controlled testing.

## Extracted Fields

Raw SerpApi results are saved to `data/raw/serpapi_wildlife_search_results.csv` with title, link, snippet, domain, result position, date retrieved, detected area, detected season, detected time of day, and a search-context confidence score.

Aggregated context is saved to:

- `data/raw/serpapi_location_context.csv`
- `data/raw/serpapi_species_context.csv`
- `data/processed/wildlife_features_enriched.csv`

## Confidence Score

The confidence score is a transparent search-context score, not a truth score:

- +3 official NPS domain
- +2 reputable outdoor, travel, or wildlife source
- +2 species and park appear in title
- +1 species and park appear in snippet
- +1 named area detected
- +1 season or time of day detected
- -2 generic or unrelated result

## Model Join

SerpApi context is aggregated by `park_name` and `species_common_name`, then joined to `wildlife_features.csv` by `park_name` and `common_name`.

Added model features include:

- `search_result_count`
- `official_source_count`
- `area_context_count`
- `season_context_count`
- `time_context_count`
- `avg_serp_confidence_score`
- `has_official_context`
- `top_mentioned_area`
- `top_mentioned_season`
- `top_mentioned_time_of_day`

The model uses `wildlife_features_enriched.csv` if it exists. Otherwise, it falls back to `wildlife_features.csv`.
