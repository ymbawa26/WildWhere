import pandas as pd

from config.settings import PROCESSED_FILES, PROCESSED_REQUIRED_COLUMNS


def test_processed_files_exist_and_have_required_columns():
    for name, path in PROCESSED_FILES.items():
        assert path.exists(), f"{path} is missing. Run `python etl/run_pipeline.py`."
        df = pd.read_csv(path)
        missing = set(PROCESSED_REQUIRED_COLUMNS[name]) - set(df.columns)
        assert not missing, f"{name} missing required columns: {sorted(missing)}"
        assert not df.empty, f"{name} should not be empty"


def test_wildlife_features_has_join_flags():
    df = pd.read_csv(PROCESSED_FILES["wildlife_features"])
    assert "weather_joined" in df.columns
    assert "visitation_joined" in df.columns
    assert df["weather_joined"].isin([True, False]).all()
    assert df["visitation_joined"].isin([True, False]).all()


def test_no_invalid_months_or_negative_visitors():
    features = pd.read_csv(PROCESSED_FILES["wildlife_features"])
    visitation = pd.read_csv(PROCESSED_FILES["visitation"])
    assert features["month"].between(1, 12).all()
    assert visitation["month"].between(1, 12).all()
    assert (visitation["recreation_visits"] >= 0).all()


def test_source_column_exists_in_processed_outputs():
    for path in PROCESSED_FILES.values():
        df = pd.read_csv(path)
        assert "source" in df.columns
        assert df["source"].notna().any()
