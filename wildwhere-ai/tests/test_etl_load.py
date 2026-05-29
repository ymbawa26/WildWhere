import sqlite3

import pandas as pd

from config.settings import DATABASE_PATH, PROCESSED_FILES
from etl.load import WAREHOUSE_TABLES, load_all_processed_data


def test_database_tables_and_row_counts_match_processed_csvs():
    db_path = load_all_processed_data(DATABASE_PATH)
    with sqlite3.connect(db_path) as conn:
        for table in WAREHOUSE_TABLES:
            expected_count = len(pd.read_csv(PROCESSED_FILES[table]))
            actual_count = conn.execute(f"SELECT COUNT(*) FROM {table};").fetchone()[0]
            assert actual_count == expected_count, table


def test_database_indexes_exist():
    load_all_processed_data(DATABASE_PATH)
    with sqlite3.connect(DATABASE_PATH) as conn:
        indexes = {
            row[1]
            for table in ["sightings", "wildlife_features", "weather", "visitation"]
            for row in conn.execute(f"PRAGMA index_list({table});").fetchall()
        }
    assert "idx_sightings_park_id" in indexes
    assert "idx_features_event_date" in indexes
    assert "idx_weather_park_date" in indexes
    assert "idx_visitation_park_year_month" in indexes
