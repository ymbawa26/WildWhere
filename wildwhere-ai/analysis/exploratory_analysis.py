import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from analysis.wildlife_metrics import (
    crowd_level_summary,
    data_quality_summary,
    missing_value_summary,
    save_analytics_outputs,
    sightings_by_park,
    sightings_by_season,
    sightings_by_species,
    sightings_by_time_of_day,
    top_park_species_combinations,
    weather_during_sightings,
)


def build_exploratory_summary() -> dict:
    outputs = save_analytics_outputs()
    return {
        "outputs": {name: str(path) for name, path in outputs.items()},
        "sightings_by_park": sightings_by_park().to_dict(orient="records"),
        "sightings_by_species": sightings_by_species().head(10).to_dict(orient="records"),
        "sightings_by_season": sightings_by_season().to_dict(orient="records"),
        "sightings_by_time_of_day": sightings_by_time_of_day().to_dict(orient="records"),
        "top_park_species": top_park_species_combinations().head(10).to_dict(orient="records"),
        "weather": weather_during_sightings().head(10).to_dict(orient="records"),
        "crowd": crowd_level_summary().to_dict(orient="records"),
        "quality": data_quality_summary().to_dict(orient="records"),
        "missing_values": missing_value_summary().head(10).to_dict(orient="records"),
    }


if __name__ == "__main__":
    summary = build_exploratory_summary()
    print("Analytics outputs written:")
    for name, path in summary["outputs"].items():
        print(f"- {name}: {path}")
