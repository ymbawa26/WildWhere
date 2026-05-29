# Processed Data Dictionary

## `parks_clean.csv`

- `park_id` TEXT, derived: Stable readable park key.
- `park_code` TEXT, raw: NPS park code.
- `park_name` TEXT, raw: Official park name.
- `state` TEXT, raw: State or states.
- `latitude` REAL, raw-cleaned: Representative latitude.
- `longitude` REAL, raw-cleaned: Representative longitude.
- `acres` REAL, raw-cleaned: Park acreage when available.
- `designation` TEXT, raw: NPS designation.
- `official_url` TEXT, raw: Official NPS URL.
- `source` TEXT, raw: Source label.

## `species_clean.csv`

- `species_id` TEXT, derived: Stable target-species key.
- `common_name` TEXT, derived: Canonical target common name.
- `scientific_name` TEXT, derived: Canonical scientific name used for analysis.
- `category` TEXT, raw-cleaned: NPSpecies category when available.
- `source` TEXT, raw/derived: Source labels used to support the species row.

## `sightings_clean.csv`

- `sighting_id` TEXT, derived: Unique sighting key.
- `occurrence_id` TEXT, raw: GBIF occurrence identifier.
- `park_id` TEXT, derived: Park key mapped from raw park code.
- `species_id` TEXT, derived: Target species key.
- `scientific_name` TEXT, raw-cleaned: GBIF scientific name.
- `common_name` TEXT, derived: Canonical target common name.
- `event_date` DATE, raw-cleaned: Parsed observation date.
- `year` INTEGER, derived from event date.
- `month` INTEGER, derived from event date.
- `season` TEXT, derived from month.
- `time_of_day` TEXT, derived from event timestamp when present; otherwise `unknown`.
- `decimal_latitude` REAL, raw-cleaned: Observation latitude.
- `decimal_longitude` REAL, raw-cleaned: Observation longitude.
- `coordinate_uncertainty` REAL, raw-cleaned: GBIF coordinate uncertainty in meters when available.
- `basis_of_record` TEXT, raw: GBIF record basis.
- `location_filter_method` TEXT, raw: Method used to retrieve the record.
- `source` TEXT, raw: Source label.
- `license` TEXT, raw: GBIF record license.
- `data_quality_flag` TEXT, derived: Primary quality flag.

## `weather_clean.csv`

- `weather_id` TEXT, derived: Unique park-station-date key.
- `park_id` TEXT, derived: Park key.
- `station_id` TEXT, raw: NOAA station ID.
- `date` DATE, raw-cleaned: Weather observation date.
- `temperature_max` REAL, raw-cleaned: Daily maximum temperature.
- `temperature_min` REAL, raw-cleaned: Daily minimum temperature.
- `temperature_avg` REAL, derived from max and min temperatures.
- `precipitation` REAL, raw-cleaned: Daily precipitation.
- `snowfall` REAL, raw-cleaned: Daily snowfall when available.
- `wind_speed` REAL, raw-cleaned: Average wind speed when available.
- `source` TEXT, raw: Source label.

## `visitation_clean.csv`

- `visit_id` TEXT, derived: Unique park-year-month key.
- `park_id` TEXT, derived: Park key.
- `park_name` TEXT, raw-cleaned: Park name from NPS Stats.
- `year` INTEGER, raw-cleaned: Visit year.
- `month` INTEGER, raw-cleaned: Visit month.
- `recreation_visits` REAL, raw-cleaned: Monthly recreation visits.
- `crowd_level` TEXT, derived: Park-specific low, medium, or high monthly visitation level.
- `source` TEXT, raw: Source label.

## `wildlife_features.csv`

- `sighting_id` TEXT, derived: Unique sighting key.
- `park_id` TEXT, derived: Park key.
- `park_name` TEXT, joined from parks.
- `state` TEXT, joined from parks.
- `species_id` TEXT, derived: Species key.
- `common_name` TEXT, derived: Canonical target common name.
- `scientific_name` TEXT, raw-cleaned: GBIF scientific name.
- `category` TEXT, joined from species.
- `event_date` DATE, raw-cleaned: Parsed sighting date.
- `year` INTEGER, derived from event date.
- `month` INTEGER, derived from event date.
- `season` TEXT, derived from month.
- `time_of_day` TEXT, derived from timestamp when available.
- `decimal_latitude` REAL, raw-cleaned: Observation latitude.
- `decimal_longitude` REAL, raw-cleaned: Observation longitude.
- `coordinate_uncertainty` REAL, raw-cleaned: Coordinate uncertainty in meters.
- `temperature_max` REAL, joined from weather.
- `temperature_min` REAL, joined from weather.
- `temperature_avg` REAL, joined from weather.
- `precipitation` REAL, joined from weather.
- `snowfall` REAL, joined from weather.
- `wind_speed` REAL, joined from weather.
- `recreation_visits` REAL, joined from visitation.
- `crowd_level` TEXT, joined from visitation.
- `basis_of_record` TEXT, raw: GBIF basis of record.
- `location_filter_method` TEXT, raw: Acquisition spatial filter method.
- `data_quality_flag` TEXT, derived: Main data quality flag.
- `source` TEXT, raw: Source label.
- `weather_joined` BOOLEAN, derived: Whether matching weather context was found.
- `visitation_joined` BOOLEAN, derived: Whether matching visitation context was found.
