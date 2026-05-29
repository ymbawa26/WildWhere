import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.settings import DATABASE_PATH


QUERIES_PATH = Path(__file__).resolve().parents[1] / "database" / "queries.sql"


def load_sql_queries() -> dict[str, str]:
    text = QUERIES_PATH.read_text()
    chunks = [chunk.strip() for chunk in text.split(";") if chunk.strip()]
    queries = {}
    for index, chunk in enumerate(chunks, start=1):
        title = chunk.splitlines()[0].replace("--", "").strip()
        sql = "\n".join(line for line in chunk.splitlines() if not line.strip().startswith("--")).strip()
        queries[f"{index}. {title}"] = sql
    return queries


def run_query(query: str, db_path: Path = DATABASE_PATH) -> pd.DataFrame:
    if not db_path.exists():
        raise FileNotFoundError("Missing SQLite database. Run `python etl/run_pipeline.py`.")
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(query, conn)


def run_all_queries(db_path: Path = DATABASE_PATH) -> dict[str, pd.DataFrame]:
    return {name: run_query(query, db_path=db_path) for name, query in load_sql_queries().items()}
