# ETL Pipeline

Step 3 turns the Step 2 raw data layer into analysis-ready CSVs and a SQLite data warehouse. It does not build the dashboard, machine learning model, or AI insight layer.

## Architecture

```text
data/raw/              Source-aligned CSVs from Step 2
etl/extract.py         Raw file loading and required-column checks
etl/transform.py       Pandas cleaning, IDs, dates, joins, feature table
etl/load.py            SQLite initialization and table loading
etl/quality_checks.py  Processed data validation and quality report
data/processed/        Clean analysis-ready CSVs
database/wildwhere.db  SQLite warehouse
```

Run the full pipeline:

```bash
python etl/run_pipeline.py
```

## Cleaning Decisions

- Column names are standardized to snake case.
- Text fields are stripped of extra whitespace.
- Fully duplicated rows are removed.
- Stable readable IDs are created for parks, species, sightings, weather, and visits.
- Source fields are preserved.
- Sightings without usable event dates or coordinates are dropped because they cannot support temporal or spatial analysis.
- Bounding-box GBIF records are kept and flagged instead of being treated as official in-park observations.
- Missing weather fields are preserved as missing, not filled.
- `crowd_level` uses park-specific monthly visitation quantiles.

## Join Logic

`wildlife_features.csv` joins:

- sightings to parks on `park_id`
- sightings to species on `species_id`
- sightings to weather on `park_id` and `event_date = date`
- sightings to visitation on `park_id`, `year`, and `month`

Weather and visitation joins are left joins. A wildlife sighting is not dropped when contextual weather or visitation data is missing. The fields `weather_joined` and `visitation_joined` make join success explicit.

## Assumptions And Limitations

- GBIF records are reported observations, not confirmed wildlife presence, true population density, or real-time tracking.
- Step 2 GBIF data uses bounding boxes near parks, not official park boundaries.
- NOAA stations are representative nearby stations and may not reflect all habitats or elevations in a park.
- NPS visitation is park-level monthly data, not trail-level observation effort.
- The feature table is for historical observation patterns and later analysis, not real-time prediction.
