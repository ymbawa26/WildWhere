# Warehouse Export Schema

SQLite remains the local warehouse for WildWhere AI. The `warehouse/` scripts add optional export paths for BigQuery and Snowflake.

## Tables

- `parks`
- `species`
- `park_species_eligibility`
- `sightings`
- `weather`
- `visitation`
- `wildlife_features`
- `wildlife_features_enriched`
- `model_predictions_log` if created in a future workflow

## Commands

```bash
python warehouse/export_sqlite.py
python warehouse/export_bigquery.py
python warehouse/export_snowflake.py
```

## BigQuery Environment Variables

- `GOOGLE_APPLICATION_CREDENTIALS`
- `BIGQUERY_PROJECT_ID`
- `BIGQUERY_DATASET`

## Snowflake Environment Variables

- `SNOWFLAKE_ACCOUNT`
- `SNOWFLAKE_USER`
- `SNOWFLAKE_PASSWORD`
- `SNOWFLAKE_WAREHOUSE`
- `SNOWFLAKE_DATABASE`
- `SNOWFLAKE_SCHEMA`

Credentials are never hardcoded. Exporters skip gracefully when credentials or optional packages are missing.
