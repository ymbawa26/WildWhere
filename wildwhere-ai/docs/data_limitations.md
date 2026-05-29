# Data Limitations

WildWhere AI uses public observation and park datasets. These sources are valuable, but they must be interpreted carefully.

## Wildlife Occurrence Data

GBIF records are observation records, not complete population data. A high number of records may reflect observer activity, road access, phone coverage, or platform participation rather than true animal abundance.

iNaturalist and other GBIF-contributing datasets may carry observer bias. Popular trails, roads, charismatic species, and active seasons can be overrepresented.

Coordinates may have uncertainty. Some records include coordinate uncertainty, while others do not. Missing uncertainty should not be treated as high precision.

Step 2 uses bounding boxes around target parks. This is a practical acquisition method, but it can include areas outside official park boundaries. The field `location_filter_method` is included so downstream ETL can distinguish bounding-box records from future boundary-filtered records.

Wildlife sightings do not equal wildlife abundance, confirmed wildlife presence, or real-time tracking.

## NPSpecies Reference Data

NPSpecies lists are maintained over time and may include statuses such as present, probably present, unconfirmed, historical, not in park, or in review. These records are reference evidence, not a complete live inventory.

Absence from a species list should not be used as proof that a species never occurs in or near a park.

## Park Metadata

Park coordinates in the raw metadata are representative points, not official park polygons. Spatial joins against actual boundaries are deferred to a later ETL step.

## Visitation Data

NPS visitation data is park-level and monthly. It does not describe visitor movement inside a park, time of day, trail-level crowding, or wildlife-viewing effort.

Visitation may help contextualize reporting patterns, but it should not be interpreted as a direct measure of wildlife observation effort.

## Weather Data

Weather stations may be near parks rather than inside them. Large elevation ranges and microclimates mean a single station can be a poor proxy for some habitats.

Daily summaries are useful for broad context but are not real-time weather, trail conditions, or local habitat conditions.

## Product Language

The project should use careful wording:

- reported occurrence patterns
- near-park occurrence data
- historical reporting patterns
- estimated sighting likelihood

The project should avoid inaccurate wording:

- confirmed sighting promise
- true population density
- real-time tracking
- real-time wildlife prediction
