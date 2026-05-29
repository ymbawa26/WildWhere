import pandas as pd

from config.settings import RAW_FILES, REQUIRED_COLUMNS, STEP2_DATASETS


def test_step2_raw_files_have_required_columns():
    for name in STEP2_DATASETS:
        path = RAW_FILES[name]
        assert path.exists(), f"{name} is missing. Run `python acquisition/run_acquisition.py --force`."
        df = pd.read_csv(path)
        missing = set(REQUIRED_COLUMNS[name]) - set(df.columns)
        assert not missing, f"{name} missing required columns: {sorted(missing)}"


def test_step2_raw_files_have_rows():
    for name in STEP2_DATASETS:
        df = pd.read_csv(RAW_FILES[name])
        assert len(df) > 0, f"{name} has no rows."


def test_visitation_months_are_valid():
    df = pd.read_csv(RAW_FILES["nps_visitation_monthly"])
    assert pd.to_numeric(df["month"], errors="coerce").between(1, 12).all()
    assert (pd.to_numeric(df["recreation_visits"], errors="coerce") >= 0).all()


def test_weather_dates_are_parseable():
    df = pd.read_csv(RAW_FILES["noaa_weather_daily"])
    assert pd.to_datetime(df["date"], errors="coerce").notna().all()
