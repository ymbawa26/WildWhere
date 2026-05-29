import pandas as pd

from config.settings import RAW_FILES, REQUIRED_COLUMNS


def test_required_csv_files_exist():
    for path in RAW_FILES.values():
        assert path.exists(), f"Missing expected data file: {path}"


def test_required_columns_present():
    for name, path in RAW_FILES.items():
        df = pd.read_csv(path)
        missing = set(REQUIRED_COLUMNS[name]) - set(df.columns)
        assert not missing, f"{name} missing columns: {missing}"


def test_duplicate_ids_absent():
    id_columns = {
        "parks": "park_code",
        "visitation": "visitation_id",
        "sightings": "sighting_id",
        "weather": "weather_id",
    }
    for name, id_column in id_columns.items():
        df = pd.read_csv(RAW_FILES[name])
        assert not df[id_column].duplicated().any(), f"{name} has duplicate {id_column} values"


def test_critical_fields_not_null():
    critical_fields = {
        "parks": ["park_code", "park_name", "latitude", "longitude"],
        "visitation": ["visitation_id", "park_code", "year", "recreation_visits"],
        "sightings": ["sighting_id", "park_code", "scientific_name", "decimal_latitude", "decimal_longitude"],
        "weather": ["weather_id", "park_code", "station_id", "date"],
    }
    for name, columns in critical_fields.items():
        df = pd.read_csv(RAW_FILES[name])
        assert not df[columns].isnull().any().any(), f"{name} has nulls in critical fields"
