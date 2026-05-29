# Manual Download Instructions

Most Step 2 datasets are automated through public APIs. These instructions document fallback paths if an API is unavailable or if a future reviewer wants to reproduce the raw layer manually.

## GBIF Occurrence Records

Automated file: `data/raw/gbif_occurrences.csv`

Fallback:

1. Go to https://www.gbif.org/occurrence/search
2. Filter country to United States.
3. Filter to the target scientific names listed in `config/settings.py`.
4. Apply a geographic filter near each target park. If using bounding boxes, record that method in `location_filter_method`.
5. Export records with coordinates and licenses included.
6. Save the normalized CSV as `data/raw/gbif_occurrences.csv`.
7. Run `python acquisition/validate_raw_data.py`.

## NPSpecies Reference Records

Automated file: `data/raw/nps_species_reference.csv`

Fallback:

1. Visit https://irma.nps.gov/NPSpecies/
2. Search each target park.
3. Download mammal and bird species lists with details when available.
4. Normalize fields to the schema in `docs/data_sources.md`.
5. Save as `data/raw/nps_species_reference.csv`.
6. Run `python acquisition/validate_raw_data.py`.

## NPS Park Metadata

Automated file: `data/raw/nps_parks.csv`

Fallback:

1. Get an API key from https://www.nps.gov/subjects/developer/get-started.htm
2. Export park metadata from `https://developer.nps.gov/api/v1/parks`.
3. Use target park codes `yell,grte,glac,olym,mora`.
4. Save normalized metadata as `data/raw/nps_parks.csv`.
5. Run `python acquisition/validate_raw_data.py`.

## NPS Monthly Visitation

Automated file: `data/raw/nps_visitation_monthly.csv`

Fallback:

1. Go to https://irma.nps.gov/Stats/
2. Open Visitor Use Statistics reports or exports.
3. Export monthly recreation visits for target park codes `YELL`, `GRTE`, `GLAC`, `OLYM`, and `MORA`.
4. Normalize columns to `park_name`, `park_code`, `year`, `month`, `recreation_visits`, `source`, `source_url`, `date_accessed`, and `license_usage_note`.
5. Save as `data/raw/nps_visitation_monthly.csv`.
6. Run `python acquisition/validate_raw_data.py`.

## NOAA Daily Weather

Automated files:

- `data/raw/noaa_weather_daily.csv`
- `data/raw/weather_station_mapping.csv`

Fallback:

1. Go to https://www.ncei.noaa.gov/access/services/data/v1
2. Use dataset `daily-summaries`.
3. Download daily records for the station IDs listed in `data/raw/weather_station_mapping.csv`.
4. Include daily maximum temperature, daily minimum temperature, precipitation, snowfall, and wind speed when available.
5. Save normalized weather rows as `data/raw/noaa_weather_daily.csv`.
6. Run `python acquisition/validate_raw_data.py`.
