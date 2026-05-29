-- 1. Total reported sightings by park
SELECT
    park_name,
    COUNT(*) AS sighting_count
FROM wildlife_features
GROUP BY park_name
ORDER BY sighting_count DESC;

-- 2. Total reported sightings by species
SELECT
    common_name,
    scientific_name,
    COUNT(*) AS sighting_count
FROM wildlife_features
GROUP BY common_name, scientific_name
ORDER BY sighting_count DESC;

-- 3. Top reported species per park
WITH species_counts AS (
    SELECT
        park_name,
        common_name,
        COUNT(*) AS sighting_count,
        RANK() OVER (PARTITION BY park_name ORDER BY COUNT(*) DESC) AS species_rank
    FROM wildlife_features
    GROUP BY park_name, common_name
)
SELECT park_name, common_name, sighting_count
FROM species_counts
WHERE species_rank = 1
ORDER BY park_name;

-- 4. Reported sightings by season
SELECT
    season,
    COUNT(*) AS sighting_count
FROM wildlife_features
GROUP BY season
ORDER BY
    CASE season
        WHEN 'winter' THEN 1
        WHEN 'spring' THEN 2
        WHEN 'summer' THEN 3
        WHEN 'fall' THEN 4
        ELSE 5
    END;

-- 5. Reported sightings by time of day
SELECT
    time_of_day,
    COUNT(*) AS sighting_count
FROM wildlife_features
GROUP BY time_of_day
ORDER BY sighting_count DESC;

-- 6. Weather patterns during reported sightings
SELECT
    common_name,
    COUNT(*) AS sightings_with_weather,
    ROUND(AVG(temperature_avg), 2) AS avg_temperature_c,
    ROUND(AVG(precipitation), 2) AS avg_precipitation_mm,
    ROUND(AVG(snowfall), 2) AS avg_snowfall_mm
FROM wildlife_features
WHERE weather_joined = 1
GROUP BY common_name
ORDER BY sightings_with_weather DESC;

-- 7. Visitation crowd level and reported sighting frequency
SELECT
    crowd_level,
    COUNT(*) AS sighting_count,
    ROUND(AVG(recreation_visits), 0) AS avg_monthly_recreation_visits
FROM wildlife_features
WHERE visitation_joined = 1
GROUP BY crowd_level
ORDER BY sighting_count DESC;

-- 8. Species distribution across parks
SELECT
    common_name,
    COUNT(DISTINCT park_id) AS parks_with_records,
    COUNT(*) AS sighting_count
FROM wildlife_features
GROUP BY common_name
ORDER BY parks_with_records DESC, sighting_count DESC;

-- 9. Monthly reported sighting trends
SELECT
    year,
    month,
    COUNT(*) AS sighting_count
FROM wildlife_features
GROUP BY year, month
ORDER BY year, month;

-- 10. Data quality summary by source
SELECT
    source,
    data_quality_flag,
    COUNT(*) AS record_count
FROM wildlife_features
GROUP BY source, data_quality_flag
ORDER BY source, record_count DESC;
