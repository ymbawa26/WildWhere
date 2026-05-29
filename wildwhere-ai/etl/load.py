import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.settings import DATABASE_PATH, PROCESSED_FILES


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "database" / "schema.sql"


def initialize_database(db_path: Path = DATABASE_PATH) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(SCHEMA_PATH.read_text())
    return db_path


def load_dataframe_to_table(df: pd.DataFrame, table_name: str, db_path: Path = DATABASE_PATH) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        df.to_sql(table_name, conn, if_exists="append", index=False)


def load_all_processed_data(db_path: Path = DATABASE_PATH) -> Path:
    initialize_database(db_path)
    for table in WAREHOUSE_TABLES:
        df = pd.read_csv(PROCESSED_FILES[table])
        load_dataframe_to_table(df, table, db_path=db_path)
        print(f"Loaded {len(df):,} rows into `{table}`")
    validate_database_load(db_path=db_path)
    return db_path


def validate_database_load(db_path: Path = DATABASE_PATH) -> dict[str, int]:
    expected = {table: len(pd.read_csv(PROCESSED_FILES[table])) for table in WAREHOUSE_TABLES}
    with sqlite3.connect(db_path) as conn:
        table_names = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%';"
            ).fetchall()
        }
        missing_tables = sorted(set(expected) - table_names)
        if missing_tables:
            raise RuntimeError(f"Database is missing expected tables: {missing_tables}")

        counts = {}
        for table, expected_count in expected.items():
            actual_count = conn.execute(f"SELECT COUNT(*) FROM {table};").fetchone()[0]
            counts[table] = actual_count
            if actual_count != expected_count:
                raise RuntimeError(f"Table `{table}` has {actual_count} rows; expected {expected_count}.")
    return counts
WAREHOUSE_TABLES = ["parks", "species", "sightings", "weather", "visitation", "wildlife_features"]

