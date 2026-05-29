# WildWhere AI

Live project: https://wildwhere-ai.vercel.app

WildWhere AI is a portfolio-grade wildlife intelligence platform for U.S. national parks. It uses real public biodiversity, weather, visitation, and park datasets to analyze historical reported wildlife observation patterns with a responsible analytics and machine learning workflow.

It does not predict confirmed wildlife presence, real-time tracking, or true population density.

## Why This Exists

Wildlife travel advice is often anecdotal. WildWhere AI treats the question as a data product: collect public records, validate them, transform them into a SQL warehouse, build reusable analytics, train an honest model, and expose the results in a polished Streamlit dashboard.

Target parks: Yellowstone, Grand Teton, Glacier, Olympic, and Mount Rainier.

## Tech Stack

Python, Pandas, SQL, SQLite, scikit-learn, Streamlit, Plotly, Pytest, GBIF, NPSpecies, NPS Visitor Use Statistics, and NOAA/NCEI Daily Summaries.

## Architecture

```text
acquisition/        Public API ingestion and raw validation
data/raw/           Source-aligned public datasets
etl/                Extract, transform, load, and quality checks
data/processed/     Clean analysis-ready CSVs
database/           SQLite schema, warehouse, and SQL queries
analysis/           Pandas and SQL analytics functions
models/             ML training, metrics, and prediction API
ai/                 Local rule-based insight generation
app/                Streamlit dashboard
tests/              End-to-end project validation
```

## Data Sources

- GBIF Occurrence API: near-park reported wildlife occurrence records
- NPSpecies IRMA API: official park species reference records
- NPS Visitor Use Statistics: monthly recreation visits
- NOAA/NCEI Daily Summaries: representative nearby weather stations
- NPS park references and NPS Developer API path for metadata

## ETL And SQL Layer

The ETL pipeline reads raw CSVs, standardizes schemas, parses dates, creates stable IDs, flags data quality issues, and loads six SQLite tables:

```text
parks
species
sightings
weather
visitation
wildlife_features
```

`database/queries.sql` includes portfolio SQL queries for park totals, species totals, seasonal patterns, time-of-day patterns, weather context, crowd-level context, and data quality summaries.

## Machine Learning

The model estimates a low, medium, or high historical reported-sighting likelihood category based on park, species, season, time of day, weather, visitation, and data quality fields. It is a pattern model over reported observations, not a wildlife presence detector.

## Dashboard Pages

- Overview: project metrics, source summary, top species, park totals, seasonal pattern
- Wildlife Explorer: filters, charts, record table, coordinate map
- Prediction Tool: estimated likelihood category with transparent caveat
- SQL Insights: selectable SQL queries and live results
- Data Transparency: source list, quality flags, missing values, join rates, limitations

## Review The Project

The deployed Vercel preview is the clean public entry point:

https://wildwhere-ai.vercel.app

The repository also includes the full Streamlit application source in `app/`, the trained model artifact in `models/`, and the reproducible data pipeline in `etl/`.

## Rebuild And Validate

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python etl/run_pipeline.py
python models/train_model.py
```

Full checks:

```bash
python scripts/run_all_checks.py
```

## Optional SerpApi Enrichment

SerpApi adds supplemental public search context such as named wildlife viewing areas, seasonal mentions, and public source signals. It is not scientific ground truth and does not replace GBIF, NPSpecies, NOAA, or NPS visitation.

```bash
export SERPAPI_API_KEY="your_key_here"
python enrichment/run_serp_enrichment.py
python enrichment/validate_serp_data.py
python etl/quality_checks.py
python models/train_model.py
pytest
```

Without `SERPAPI_API_KEY`, enrichment skips live search gracefully and writes schema-valid zero-context features.

## Deploy

The public portfolio preview is deployed through Vercel:

```text
https://wildwhere-ai.vercel.app
```

For a full Streamlit deployment, use this app entry point:

```text
app/main.py
```

See `docs/deployment.md` for setup and troubleshooting.

## Screenshots To Add

- Overview page with headline metrics
- Wildlife Explorer filtered to one species and park
- Prediction Tool result card
- SQL Insights query and result table
- Data Transparency quality section

## Limitations

GBIF records are observation-based and biased by human reporting. Bounding boxes may include areas outside official park boundaries. Weather stations are representative nearby stations. NPS visitation is monthly park-level context, not trail-level observation effort.

## Resume Bullets

- Built WildWhere AI, an AI-powered wildlife intelligence platform using Python, Pandas, SQL, SQLite, ETL pipelines, and machine learning to analyze real public wildlife, weather, visitation, and park datasets across U.S. national parks.
- Developed an end-to-end data pipeline that extracts, validates, transforms, and loads public biodiversity and park datasets into a SQL database, with automated data-quality checks, analytics queries, and a deployed Streamlit dashboard.
