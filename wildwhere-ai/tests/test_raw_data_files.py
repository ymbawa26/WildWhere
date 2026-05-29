from config.settings import DATABASE_DIR, RAW_FILES, STEP2_DATASETS


def test_step2_raw_files_exist_after_acquisition():
    missing = [str(RAW_FILES[name]) for name in STEP2_DATASETS if not RAW_FILES[name].exists()]
    assert not missing, "Missing Step 2 raw files. Run `python acquisition/run_acquisition.py --force`: " + ", ".join(missing)


def test_step2_raw_files_are_not_empty():
    empty = [str(RAW_FILES[name]) for name in STEP2_DATASETS if RAW_FILES[name].exists() and RAW_FILES[name].stat().st_size == 0]
    assert not empty, "Empty Step 2 raw files found: " + ", ".join(empty)


def test_database_folder_still_intact():
    assert DATABASE_DIR.exists(), "Database folder is missing."
    assert (DATABASE_DIR / "schema.sql").exists(), "Database schema.sql is missing."
    assert (DATABASE_DIR / "init_db.py").exists(), "Database init_db.py is missing."
