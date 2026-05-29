# Data Sources

Date accessed for Step 2 raw data layer: 2026-05-28.

## GBIF Occurrence Data

Dataset name: GBIF near-park wildlife occurrence records

Source: Global Biodiversity Information Facility Occurrence API

URL: https://api.gbif.org/v1/occurrence/search

Access method: Automated API query in `acquisition/gbif_client.py`

Raw file path: `data/raw/gbif_occurrences.csv`

License/usage note: Record-level licenses are preserved in the `license` column when GBIF returns them. Downstream usage should respect each record's original dataset license.

Columns used: `occurrence_id`, `park_code`, `park_name`, `target_common_name`, `scientific_name`, `common_name`, `event_date`, `decimal_latitude`, `decimal_longitude`, `basis_of_record`, `dataset_name`, `institution_code`, `country`, `state_province`, `coordinate_uncertainty`, `license`, `source`, `source_url`, `date_accessed`, `location_filter_method`.

Known limitations: Occurrence records are observation records, not complete population data. Step 2 uses bounding boxes around parks, so records may fall near a park but outside official boundaries.

How it will be used later: Step 3 will clean, deduplicate, and spatially refine occurrence records before analytics and modeling work.

## NPSpecies Reference Data

Dataset name: NPSpecies mammal and bird reference records

Source: National Park Service NPSpecies IRMA REST API

URL: https://irmaservices.nps.gov/NPSpecies/v3/rest

Access method: Automated API query in `acquisition/nps_client.py`

Raw file path: `data/raw/nps_species_reference.csv`

License/usage note: U.S. federal public information; verify current NPS terms before redistribution.

Columns used: `park_name`, `park_code`, `category`, `common_name`, `scientific_name`, `occurrence_status`, `abundance`, `nativeness`, `record_status`, `source`, `source_url`, `date_accessed`, `license_usage_note`.

Known limitations: NPSpecies records are maintained over time and may include statuses such as present, probably present, unconfirmed, historical, or in review. Absence from a list should not be treated as proof of absence.

How it will be used later: The reference list will help validate whether GBIF occurrences are plausible for a park and flag records that need review.

## NPS Park Metadata

Dataset name: NPS park metadata

Source: National Park Service park references and, when available, NPS Developer API

URL: https://developer.nps.gov/api/v1/parks

Access method: `acquisition/nps_client.py`; uses `NPS_API_KEY` if available, otherwise writes official-reference fields from project configuration.

Raw file path: `data/raw/nps_parks.csv`

License/usage note: U.S. federal public information; verify current NPS terms before redistribution.

Columns used: `park_code`, `park_name`, `state`, `latitude`, `longitude`, `acres`, `designation`, `description`, `official_url`, `source`, `source_url`, `date_accessed`, `license_usage_note`.

Known limitations: Coordinates are representative park coordinates, not complete boundaries. Official boundary joins are intentionally deferred to later spatial ETL.

How it will be used later: Park metadata anchors joins, labels, filters, mapping, and validation.

## NPS Monthly Visitation

Dataset name: NPS monthly recreation visits

Source: National Park Service Visitor Use Statistics IRMA REST API

URL: https://irmaservices.nps.gov/Stats/v1/visitation

Access method: Automated API query in `acquisition/visitation_client.py`

Raw file path: `data/raw/nps_visitation_monthly.csv`

License/usage note: U.S. federal public information; verify current NPS terms before redistribution.

Columns used: `park_name`, `park_code`, `year`, `month`, `recreation_visits`, `source`, `source_url`, `date_accessed`, `license_usage_note`.

Known limitations: Visitation is park-level monthly reporting. It does not describe trail-level crowding or visitor distribution inside parks.

How it will be used later: Visitation will provide context for seasonality, observer bias, and reporting intensity.

## NOAA Daily Weather

Dataset name: NOAA/NCEI daily weather summaries near target parks

Source: NOAA National Centers for Environmental Information Daily Summaries

URL: https://www.ncei.noaa.gov/access/services/data/v1

Access method: Automated API query in `acquisition/weather_client.py`

Raw file path: `data/raw/noaa_weather_daily.csv`

License/usage note: NOAA/NCEI public data; verify dataset-specific terms before redistribution.

Columns used: `station_id`, `nearest_park`, `park_code`, `date`, `temperature_max`, `temperature_min`, `precipitation`, `snowfall`, `wind_speed`, `source`, `source_url`, `date_accessed`, `license_usage_note`.

Known limitations: Stations are representative nearby stations. They may not be inside the park and may not reflect all elevations, habitats, or microclimates.

How it will be used later: Weather will support seasonal context and later feature engineering.

## Weather Station Mapping

Dataset name: Park-to-weather-station mapping

Source: NOAA station metadata and Step 1 station selection review

URL: https://www.ncei.noaa.gov/access/services/data/v1

Access method: Generated by `acquisition/weather_client.py` from documented station choices in `config/settings.py`

Raw file path: `data/raw/weather_station_mapping.csv`

License/usage note: NOAA/NCEI public data; verify dataset-specific terms before redistribution.

Columns used: `park_code`, `park_name`, `station_id`, `station_name`, `distance_km`, `selection_method`, `source`, `source_url`, `date_accessed`, `license_usage_note`.

Known limitations: "Nearest representative station" is not the same as an official park weather surface. Step 3 should revisit station choice and consider multiple stations for large or mountainous parks.

How it will be used later: The mapping makes weather joins traceable and lets the dashboard communicate station proximity.
