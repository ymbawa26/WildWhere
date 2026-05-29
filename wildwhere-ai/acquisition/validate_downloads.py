import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.settings import RAW_FILES, REQUIRED_COLUMNS


def validate_csv(name: str, path: Path, required_columns: list[str]) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing required data file: {path}")

    df = pd.read_csv(path)
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
    if df.empty:
        raise ValueError(f"{name} has no rows: {path}")

    return {
        "dataset": name,
        "path": str(path),
        "rows": len(df),
        "columns": len(df.columns),
    }


def validate_all_downloads() -> list[dict]:
    summaries = []
    for name, path in RAW_FILES.items():
        summary = validate_csv(name, path, REQUIRED_COLUMNS[name])
        summaries.append(summary)
        print(f"{name}: {summary['rows']:,} rows, {summary['columns']} columns")
    return summaries


if __name__ == "__main__":
    validate_all_downloads()
