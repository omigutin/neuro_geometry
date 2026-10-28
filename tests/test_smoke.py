""" Smoke: пакет импортируется, публичный API на месте. """

import neuro_geometry


def test_public_api() -> None:
    assert set(neuro_geometry.__all__) == {
        "Line",
        "LineDirection",
        "Point",
        "Quadrangle",
        "Rectangle",
        "Triangle",
        "batch",
        "round_half_up",
        "to_contour",
    }
    assert neuro_geometry.__version__ == "0.2.0"
