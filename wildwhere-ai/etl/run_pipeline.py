import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from etl.extract import load_all_raw_data
from etl.load import load_all_processed_data
from etl.quality_checks import check_processed_data
from etl.transform import transform_all, write_processed_data


def run_pipeline() -> None:
    print("Extracting raw data...")
    raw_dfs = load_all_raw_data()
    for name, df in raw_dfs.items():
        print(f"  {name}: {len(df):,} rows")

    print("Transforming raw data into processed tables...")
    cleaned_dfs = transform_all(raw_dfs)
    write_processed_data(cleaned_dfs)

    print("Running processed data quality checks...")
    check_processed_data()

    print("Loading processed tables into SQLite...")
    db_path = load_all_processed_data()
    print(f"Step 3 ETL pipeline completed successfully: {db_path}")


if __name__ == "__main__":
    run_pipeline()
