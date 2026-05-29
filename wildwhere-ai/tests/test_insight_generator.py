from ai.insight_generator import (
    generate_data_quality_note,
    generate_park_summary,
    generate_prediction_explanation,
    generate_species_insight,
)


def test_species_and_park_insights_are_grounded():
    text = generate_species_insight("Bison", "Yellowstone National Park")
    assert "Bison" in text
    assert "confirmed wildlife presence" in text.lower()


def test_park_summary_and_quality_note():
    assert "Yellowstone National Park" in generate_park_summary("Yellowstone National Park")
    assert "bounding" in generate_data_quality_note().lower()


def test_prediction_explanation_uses_disclaimer():
    text = generate_prediction_explanation(
        {
            "predicted_category": "medium",
            "confidence": 0.6,
            "feature_summary": {"common_name": "Moose", "park_name": "Grand Teton National Park", "season": "summer"},
        }
    )
    assert "medium" in text
    assert "pattern estimate" in text
