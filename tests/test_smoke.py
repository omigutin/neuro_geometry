""" Smoke: пакет импортируется, публичный API на месте. """

import neuro_geometry


def test_public_api() -> None:
    assert set(neuro_geometry.__all__) == {
        "Contour", "Line", "LineDirection", "Point", "Quadrangle", "Rectangle", "Triangle"
    }
    assert neuro_geometry.__version__
