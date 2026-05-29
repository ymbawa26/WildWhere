from pathlib import Path

import pandas as pd
import pytest

from etl import extract


def test_raw_files_can_be_loaded_as_dataframes():
    loaded = extract.load_all_raw_data()
    assert set(loaded) == {"parks", "species", "sightings", "weather", "visitation"}
    assert all(isinstance(df, pd.DataFrame) for df in loaded.values())
    assert all(not df.empty for df in loaded.values())


def test_missing_raw_file_fails_clearly(monkeypatch, tmp_path):
    missing_path = tmp_path / "missing.csv"
    monkeypatch.setitem(extract.RAW_FILES, "nps_parks", missing_path)
    with pytest.raises(extract.RawDataError, match="Missing raw dataset"):
        extract.load_raw_parks()
