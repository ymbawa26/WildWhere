# Data Dictionary

## `park_metadata.csv`

Source: National Park Service public park metadata and official park references.

Columns:

- `park_code`: NPS alpha code used as the park primary key.
- `park_name`: Official park name.
- `state`: State or states associated with the park.
- `latitude`: Representative park latitude.
- `longitude`: Representative park longitude.
- `area_acres`: Official park area in acres.
- `source`: Source label for traceability.

Cleaning expectations: park codes should be unique and non-null. Coordinates should be numeric and suitable for mapping, not exact boundary geometry.

## `wildlife_sightings.csv`

Source: GBIF Occurrence API.

Columns:

- `sighting_id`: Stable project ID derived from the GBIF occurrence key.
- `park_code`: Target park associated with the acquisition geometry.
- `gbif_id`: GBIF occurrence key.
- `scientific_name`: Scientific taxon name.
- `common_name`: Common name when supplied by GBIF.
- `taxon_rank`: Taxonomic rank from GBIF.
- `event_date`: Observation or identification date.
- `decimal_latitude`: Observation latitude.
- `decimal_longitude`: Observation longitude.
- `basis_of_record`: GBIF record basis, currently filtered to human observations.
- `dataset_key`: GBIF source dataset key.
- `recorded_by`: Observer or recorder when available.
- `source`: Source label for traceability.

Cleaning expectations: future ETL should remove spatial outliers, harmonize taxonomy, and flag observations with weak temporal precision.

## `visitation.csv`

Source: National Park Service Visitor Use Statistics.

Columns:

- `visitation_id`: Project key combining park and year.
- `park_code`: NPS alpha code.
- `year`: Calendar year.
- `recreation_visits`: Annual recreation visits.
- `source`: Source label for traceability.
- `source_url`: Public source location.

Cleaning expectations: visitation is reported using NPS methodology and should be treated as an estimate. Future work should ingest a full export from IRMA rather than expanding manual reference rows.

## `weather.csv`

Source: NOAA NCEI Daily Summaries.

Columns:

- `weather_id`: Project key combining park and date.
- `park_code`: NPS alpha code.
- `station_id`: NOAA station ID used for the park.
- `date`: Observation date.
- `tmax_c`: Daily maximum temperature in Celsius.
- `tmin_c`: Daily minimum temperature in Celsius.
- `precipitation_mm`: Daily precipitation in millimeters.
- `source`: Source label for traceability.

Cleaning expectations: future ETL should add station distance metadata, fill or flag missing weather measurements, and evaluate whether multiple stations are needed per park.

## Relationships

- `parks.park_code` is the parent key for sightings, weather, and visitation.
- `species.scientific_name` is derived from unique GBIF sighting names.
- Future modeling tables should join sightings to weather by `park_code` and date after temporal cleaning.
