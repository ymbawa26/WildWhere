import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


COMMANDS = [
    [sys.executable, "etl/run_pipeline.py"],
    [sys.executable, "enrichment/run_serp_enrichment.py"],
    [sys.executable, "enrichment/validate_serp_data.py"],
    [sys.executable, "etl/quality_checks.py"],
    [sys.executable, "analysis/exploratory_analysis.py"],
    [sys.executable, "models/train_model.py"],
    [sys.executable, "models/generate_prediction_grid.py"],
    [sys.executable, "-m", "pytest"],
]


def run_all_checks() -> None:
    for command in COMMANDS:
        print(f"\nRunning: {' '.join(command)}")
        subprocess.run(command, cwd=ROOT, check=True)
    print("\nAll WildWhere AI checks passed.")


if __name__ == "__main__":
    run_all_checks()
