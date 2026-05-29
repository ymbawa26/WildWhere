from models.predict import predict_sighting_likelihood
from validation.species_eligibility import build_park_species_eligibility, is_species_eligible


def test_bison_mount_rainier_is_blocked():
    build_park_species_eligibility()
    eligibility = is_species_eligible("Mount Rainier National Park", "Bison")
    assert eligibility["is_documented_in_park"] is False


def test_bison_yellowstone_is_allowed():
    build_park_species_eligibility()
    eligibility = is_species_eligible("Yellowstone National Park", "Bison")
    assert eligibility["is_documented_in_park"] is True


def test_unsupported_combination_does_not_use_model():
    result = predict_sighting_likelihood(
        {"park_name": "Mount Rainier National Park", "common_name": "Bison"}
    )
    assert result["likelihood_category"] == "Not supported"
    assert result["model_used"] is False


def test_blocked_prediction_returns_zero_probability():
    result = predict_sighting_likelihood(
        {"park_name": "Mount Rainier National Park", "common_name": "Bison"}
    )
    assert result["probability"] == 0
    assert result["confidence"] == 0


def test_blocked_prediction_has_professional_explanation():
    result = predict_sighting_likelihood(
        {"park_name": "Mount Rainier National Park", "common_name": "Bison"}
    )
    message = result["message"].lower()
    assert "not documented" in message
    assert "fake" not in message
    assert result["probabilities"] == {}
