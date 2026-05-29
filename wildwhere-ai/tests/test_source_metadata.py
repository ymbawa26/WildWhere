import ast
from pathlib import Path

import pandas as pd

from config.settings import DOCS_DIR, RAW_FILES, RAW_VALIDATION_REPORT, STEP2_DATASETS


def test_source_documentation_exists():
    required_docs = [
        DOCS_DIR / "data_sources.md",
        DOCS_DIR / "data_limitations.md",
        DOCS_DIR / "manual_download_instructions.md",
        DOCS_DIR / "raw_data_validation_report.md",
    ]
    missing = [str(path) for path in required_docs if not path.exists()]
    assert not missing, "Missing source documentation: " + ", ".join(missing)


def test_source_columns_are_populated():
    for name in STEP2_DATASETS:
        df = pd.read_csv(RAW_FILES[name])
        assert "source" in df.columns, f"{name} missing source column"
        assert df["source"].notna().any(), f"{name} source column is empty"


def test_validation_report_exists():
    assert RAW_VALIDATION_REPORT.exists(), "Validation report missing. Run `python acquisition/validate_raw_data.py`."
    text = RAW_VALIDATION_REPORT.read_text()
    assert "Overall status: PASS" in text


def test_no_api_keys_are_hardcoded_in_acquisition_scripts():
    acquisition_dir = Path("acquisition")
    suspicious_literals = []
    for path in acquisition_dir.glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                value = node.value
                lowered = value.lower()
                if "api_key=" in lowered or "x-api-key" in lowered:
                    suspicious_literals.append((str(path), value))
    assert not suspicious_literals, f"Potential hardcoded API key literals found: {suspicious_literals}"


def test_acquisition_scripts_import_without_crashing():
    import acquisition.gbif_client  # noqa: F401
    import acquisition.nps_client  # noqa: F401
    import acquisition.run_acquisition  # noqa: F401
    import acquisition.validate_raw_data  # noqa: F401
    import acquisition.visitation_client  # noqa: F401
    import acquisition.weather_client  # noqa: F401
