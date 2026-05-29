from pathlib import Path

from config.settings import DATABASE_PATH, PROCESSED_FILES


def test_core_artifacts_exist():
    assert Path("README.md").exists()
    assert Path("docs/deployment.md").exists()
    assert Path(".streamlit/config.toml").exists()
    assert Path("vercel.json").exists()
    assert DATABASE_PATH.exists()
    for path in PROCESSED_FILES.values():
        assert path.exists()


def test_no_fake_production_data_language_in_core_docs():
    combined = "\n".join(Path(path).read_text().lower() for path in ["README.md", "docs/data_limitations.md"])
    assert "synthetic production data" not in combined
    assert "real-time tracking" in combined
