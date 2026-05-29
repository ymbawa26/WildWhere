PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS parks (
    park_id TEXT PRIMARY KEY,
    park_code TEXT NOT NULL UNIQUE,
    park_name TEXT NOT NULL,
    state TEXT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    acres REAL,
    designation TEXT,
    official_url TEXT,
    source TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS species (
    species_id TEXT PRIMARY KEY,
    common_name TEXT NOT NULL UNIQUE,
    scientific_name TEXT NOT NULL,
    category TEXT,
    source TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sightings (
    sighting_id TEXT PRIMARY KEY,
    occurrence_id TEXT NOT NULL,
    park_id TEXT NOT NULL,
    species_id TEXT NOT NULL,
    scientific_name TEXT NOT NULL,
    common_name TEXT NOT NULL,
    event_date TEXT NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    season TEXT NOT NULL,
    time_of_day TEXT NOT NULL,
    decimal_latitude REAL NOT NULL,
    decimal_longitude REAL NOT NULL,
    coordinate_uncertainty REAL,
    basis_of_record TEXT,
    location_filter_method TEXT NOT NULL,
    source TEXT NOT NULL,
    license TEXT,
    data_quality_flag TEXT NOT NULL,
    FOREIGN KEY (park_id) REFERENCES parks (park_id),
    FOREIGN KEY (species_id) REFERENCES species (species_id)
);

CREATE TABLE IF NOT EXISTS weather (
    weather_id TEXT PRIMARY KEY,
    park_id TEXT NOT NULL,
    station_id TEXT NOT NULL,
    date TEXT NOT NULL,
    temperature_max REAL,
    temperature_min REAL,
    temperature_avg REAL,
    precipitation REAL,
    snowfall REAL,
    wind_speed REAL,
    source TEXT NOT NULL,
    FOREIGN KEY (park_id) REFERENCES parks (park_id)
);

CREATE TABLE IF NOT EXISTS visitation (
    visit_id TEXT PRIMARY KEY,
    park_id TEXT NOT NULL,
    park_name TEXT NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    recreation_visits REAL NOT NULL,
    crowd_level TEXT NOT NULL,
    source TEXT NOT NULL,
    FOREIGN KEY (park_id) REFERENCES parks (park_id),
    UNIQUE (park_id, year, month)
);

CREATE TABLE IF NOT EXISTS wildlife_features (
    sighting_id TEXT PRIMARY KEY,
    park_id TEXT NOT NULL,
    park_name TEXT,
    state TEXT,
    species_id TEXT NOT NULL,
    common_name TEXT NOT NULL,
    scientific_name TEXT NOT NULL,
    category TEXT,
    event_date TEXT NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    season TEXT NOT NULL,
    time_of_day TEXT NOT NULL,
    decimal_latitude REAL NOT NULL,
    decimal_longitude REAL NOT NULL,
    coordinate_uncertainty REAL,
    temperature_max REAL,
    temperature_min REAL,
    temperature_avg REAL,
    precipitation REAL,
    snowfall REAL,
    wind_speed REAL,
    recreation_visits REAL,
    crowd_level TEXT,
    basis_of_record TEXT,
    location_filter_method TEXT NOT NULL,
    data_quality_flag TEXT NOT NULL,
    source TEXT NOT NULL,
    weather_joined INTEGER NOT NULL,
    visitation_joined INTEGER NOT NULL,
    FOREIGN KEY (park_id) REFERENCES parks (park_id),
    FOREIGN KEY (species_id) REFERENCES species (species_id)
);

CREATE INDEX IF NOT EXISTS idx_parks_park_id ON parks (park_id);
CREATE INDEX IF NOT EXISTS idx_species_species_id ON species (species_id);
CREATE INDEX IF NOT EXISTS idx_species_common_name ON species (common_name);
CREATE INDEX IF NOT EXISTS idx_sightings_park_id ON sightings (park_id);
CREATE INDEX IF NOT EXISTS idx_sightings_species_id ON sightings (species_id);
CREATE INDEX IF NOT EXISTS idx_sightings_event_date ON sightings (event_date);
CREATE INDEX IF NOT EXISTS idx_sightings_year_month ON sightings (year, month);
CREATE INDEX IF NOT EXISTS idx_sightings_season ON sightings (season);
CREATE INDEX IF NOT EXISTS idx_sightings_time_of_day ON sightings (time_of_day);
CREATE INDEX IF NOT EXISTS idx_sightings_common_name ON sightings (common_name);
CREATE INDEX IF NOT EXISTS idx_weather_park_date ON weather (park_id, date);
CREATE INDEX IF NOT EXISTS idx_visitation_park_year_month ON visitation (park_id, year, month);
CREATE INDEX IF NOT EXISTS idx_features_park_id ON wildlife_features (park_id);
CREATE INDEX IF NOT EXISTS idx_features_species_id ON wildlife_features (species_id);
CREATE INDEX IF NOT EXISTS idx_features_event_date ON wildlife_features (event_date);
CREATE INDEX IF NOT EXISTS idx_features_year_month ON wildlife_features (year, month);
CREATE INDEX IF NOT EXISTS idx_features_season ON wildlife_features (season);
CREATE INDEX IF NOT EXISTS idx_features_time_of_day ON wildlife_features (time_of_day);
CREATE INDEX IF NOT EXISTS idx_features_common_name ON wildlife_features (common_name);
