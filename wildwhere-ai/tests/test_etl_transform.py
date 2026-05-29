import pandas as pd

from etl.extract import load_all_raw_data
from etl.transform import _season, clean_parks, clean_visitation, transform_all


def test_cleaned_columns_are_snake_case():
    raw = load_all_raw_data()
    parks = clean_parks(raw["parks"])
    assert all(column == column.lower() and " " not in column for column in parks.columns)


def test_season_logic():
    assert _season(1) == "winter"
    assert _season(4) == "spring"
    assert _season(7) == "summer"
    assert _season(10) == "fall"


def test_crowd_level_logic_creates_expected_labels():
    raw = load_all_raw_data()
    parks = clean_parks(raw["parks"])
    visitation = clean_visitation(raw["visitation"], parks)
    assert set(visitation["crowd_level"]).issubset({"low", "medium", "high"})
    assert visitation["visit_id"].is_unique


def test_transform_outputs_required_processed_frames():
    cleaned = transform_all(load_all_raw_data())
    assert {"parks", "species", "sightings", "weather", "visitation", "wildlife_features"} == set(cleaned)
    for name, df in cleaned.items():
        assert isinstance(df, pd.DataFrame), name
        assert not df.empty, name
    assert cleaned["sightings"]["sighting_id"].is_unique
    assert pd.to_datetime(cleaned["sightings"]["event_date"], errors="coerce").notna().all()
