from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config.settings import (
    RAW_FILES,
    RAW_VALIDATION_REPORT,
    REQUIRED_COLUMNS,
    STEP2_DATASETS,
    ACCEPTED_GBIF_NAME_PREFIXES,
    TARGET_PARKS,
)


@dataclass
class ValidationResult:
    dataset: str
    path: Path
    rows: int = 0
    columns: int = 0
    passed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    duplicate_rows: int = 0
    missing_summary: dict[str, int] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.failed


def _add(condition: bool, result: ValidationResult, message: str) -> None:
    if condition:
        result.passed.append(message)
    else:
        result.failed.append(message)


def _read_dataset(name: str, result: ValidationResult) -> pd.DataFrame | None:
    _add(result.path.exists(), result, "file exists")
    if not result.path.exists():
        result.failed.append(f"missing file: {result.path}")
        return None
    try:
        df = pd.read_csv(result.path)
    except Exception as exc:
        result.failed.append(f"file is not readable as CSV: {exc}")
        return None
    result.rows = len(df)
    result.columns = len(df.columns)
    result.duplicate_rows = int(df.duplicated().sum())
    result.missing_summary = {column: int(df[column].isna().sum()) for column in df.columns}
    return df


def validate_dataset(name: str) -> ValidationResult:
    result = ValidationResult(dataset=name, path=RAW_FILES[name])
    df = _read_dataset(name, result)
    if df is None:
        return result

    required = REQUIRED_COLUMNS[name]
    missing_columns = sorted(set(required) - set(df.columns))
    _add(result.rows > 0, result, "row count is greater than zero")
    _add(not missing_columns, result, f"required columns present: {', '.join(required)}")
    _add(result.duplicate_rows == 0, result, "no fully duplicated rows")
    if "source" in required:
        _add("source" in df.columns, result, "source column exists")
    if missing_columns:
        result.failed.append(f"missing columns: {missing_columns}")
        return result

    critical = [column for column in required if column not in {"source_url", "license_usage_note"}]
    for column in critical:
        _add(not df[column].isna().all(), result, f"{column} is not completely null")

    if name == "gbif_occurrences":
        gbif_checks(df, result)
    elif name == "nps_species_reference":
        nps_species_checks(df, result)
    elif name == "nps_visitation_monthly":
        visitation_checks(df, result)
    elif name == "noaa_weather_daily":
        weather_checks(df, result)
    elif name == "weather_station_mapping":
        station_mapping_checks(df, result)
    elif name == "nps_parks":
        park_checks(df, result)

    return result


def gbif_checks(df: pd.DataFrame, result: ValidationResult) -> None:
    _add(df["scientific_name"].notna().any(), result, "GBIF scientific_name exists")
    _add(df["event_date"].notna().any(), result, "GBIF event_date exists for at least some records")
    _add(df["decimal_latitude"].notna().all(), result, "GBIF latitude exists for all records")
    _add(df["decimal_longitude"].notna().all(), result, "GBIF longitude exists for all records")
    normalized_country = df["country"].fillna("").str.upper()
    _add(
        normalized_country.isin({"UNITED STATES", "UNITED STATES OF AMERICA", "US", "USA"}).all(),
        result,
        "GBIF records are in the United States",
    )
    matched = df["scientific_name"].fillna("").apply(
        lambda value: any(value.startswith(target) for target in ACCEPTED_GBIF_NAME_PREFIXES)
    )
    _add(matched.all(), result, "GBIF species match target scientific names or accepted equivalents")
    _add("coordinate_uncertainty" in df.columns, result, "GBIF coordinate uncertainty column is documented")
    if df["coordinate_uncertainty"].isna().mean() > 0.5:
        result.warnings.append("More than half of GBIF records lack coordinate uncertainty values.")
    if set(df["location_filter_method"].dropna().unique()) == {"bounding_box"}:
        result.warnings.append("GBIF records use bounding boxes and may include land outside official park boundaries.")


def nps_species_checks(df: pd.DataFrame, result: ValidationResult) -> None:
    _add(df["park_name"].notna().all(), result, "NPS species park_name exists")
    _add(df["scientific_name"].notna().all(), result, "NPS species scientific_name exists")
    _add(df["common_name"].notna().any(), result, "NPS species common_name exists where available")
    target_codes = {park["park_code"] for park in TARGET_PARKS}
    present_codes = set(df["park_code"].dropna().unique())
    missing_codes = sorted(target_codes - present_codes)
    _add(not missing_codes, result, "each target park has species records")
    if missing_codes:
        result.failed.append(f"NPS species records missing for parks: {missing_codes}")


def visitation_checks(df: pd.DataFrame, result: ValidationResult) -> None:
    year = pd.to_numeric(df["year"], errors="coerce")
    month = pd.to_numeric(df["month"], errors="coerce")
    visits = pd.to_numeric(df["recreation_visits"], errors="coerce")
    _add(year.notna().all(), result, "visitation year is numeric")
    _add(month.between(1, 12).all(), result, "visitation month is between 1 and 12")
    _add(visits.notna().all(), result, "recreation_visits is numeric")
    _add((visits >= 0).all(), result, "recreation_visits has no negative values")


def weather_checks(df: pd.DataFrame, result: ValidationResult) -> None:
    parsed_dates = pd.to_datetime(df["date"], errors="coerce")
    _add(parsed_dates.notna().all(), result, "weather date is parseable")
    for column in ["temperature_max", "temperature_min", "precipitation"]:
        numeric = pd.to_numeric(df[column], errors="coerce")
        _add(numeric.notna().any(), result, f"{column} has numeric values where available")


def station_mapping_checks(df: pd.DataFrame, result: ValidationResult) -> None:
    target_codes = {park["park_code"] for park in TARGET_PARKS}
    present_codes = set(df["park_code"].dropna().unique())
    _add(target_codes.issubset(present_codes), result, "each park has a station mapping")


def park_checks(df: pd.DataFrame, result: ValidationResult) -> None:
    _add(not df["park_code"].duplicated().any(), result, "park_code values are unique")
    _add(pd.to_numeric(df["latitude"], errors="coerce").notna().all(), result, "park latitude is numeric")
    _add(pd.to_numeric(df["longitude"], errors="coerce").notna().all(), result, "park longitude is numeric")


def write_report(results: list[ValidationResult]) -> Path:
    lines = [
        "# Raw Data Validation Report",
        "",
        "Generated by `acquisition/validate_raw_data.py`.",
        "",
        "This report validates the Step 2 raw data layer. It records row counts, passed checks, failed checks, warnings, duplicate counts, and missing-value summaries.",
        "",
    ]
    total_failures = sum(len(result.failed) for result in results)
    lines.extend(
        [
            f"Overall status: {'PASS' if total_failures == 0 else 'FAIL'}",
            f"Datasets checked: {len(results)}",
            f"Failed checks: {total_failures}",
            "",
        ]
    )
    for result in results:
        lines.extend(
            [
                f"## {result.dataset}",
                "",
                f"Path: `{result.path}`",
                f"Rows: {result.rows}",
                f"Columns: {result.columns}",
                f"Duplicate full rows: {result.duplicate_rows}",
                "",
                "Passed checks:",
            ]
        )
        lines.extend([f"- {item}" for item in result.passed] or ["- None"])
        lines.append("")
        lines.append("Failed checks:")
        lines.extend([f"- {item}" for item in result.failed] or ["- None"])
        lines.append("")
        lines.append("Warnings:")
        lines.extend([f"- {item}" for item in result.warnings] or ["- None"])
        lines.append("")
        lines.append("Missing values by column:")
        for column, missing_count in result.missing_summary.items():
            lines.append(f"- `{column}`: {missing_count}")
        lines.append("")

    RAW_VALIDATION_REPORT.parent.mkdir(parents=True, exist_ok=True)
    RAW_VALIDATION_REPORT.write_text("\n".join(lines) + "\n")
    return RAW_VALIDATION_REPORT


def validate_all_raw_data() -> list[ValidationResult]:
    results = [validate_dataset(name) for name in STEP2_DATASETS]
    report_path = write_report(results)
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"{status}: {result.dataset} ({result.rows:,} rows, {result.columns} columns)")
        for warning in result.warnings:
            print(f"  warning: {warning}")
        for failure in result.failed:
            print(f"  failure: {failure}")
    print(f"Validation report written to {report_path}")
    return results


if __name__ == "__main__":
    validation_results = validate_all_raw_data()
    if any(result.failed for result in validation_results):
        raise SystemExit(1)
