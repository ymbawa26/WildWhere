import sqlite3

from config.settings import DATABASE_PATH
from etl.load import load_all_processed_data


def test_database_initialization_success():
    db_path = load_all_processed_data(DATABASE_PATH)
    assert db_path.exists()

    with sqlite3.connect(db_path) as conn:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%';"
            ).fetchall()
        }
        assert {"parks", "species", "sightings", "weather", "visitation", "wildlife_features"}.issubset(tables)

        for table in ["parks", "species", "sightings", "weather", "visitation", "wildlife_features"]:
            count = conn.execute(f"SELECT COUNT(*) FROM {table};").fetchone()[0]
            assert count > 0, f"{table} should contain loaded records"
