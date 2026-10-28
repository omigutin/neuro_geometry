import numpy as np
import pytest

from neuro_geometry import round_half_up, to_contour


@pytest.mark.parametrize(("value", "expected"), [(2.5, 3), (3.5, 4), (-2.5, -2), (2.4999, 2), (-0.6, -1), (7, 7)])
def test_round_half_up(value: float, expected: int) -> None:
    assert round_half_up(value) == expected


def test_to_contour() -> None:
    contour = to_contour([[0.5, 1.4], [2.5, -0.5]])
    assert contour.shape == (2, 1, 2) and contour.dtype == np.int32
    assert contour.reshape(-1, 2).tolist() == [[1, 1], [3, 0]]
