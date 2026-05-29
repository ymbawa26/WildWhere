import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from etl.load import initialize_database, load_all_processed_data


if __name__ == "__main__":
    load_all_processed_data()
