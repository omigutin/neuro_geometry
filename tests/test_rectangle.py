import builtins
from typing import Any

import numpy as np
import pytest

from neuro_geometry import Point, Rectangle


def test_axis_aligned_from_box_forms() -> None:
    for box in ([0, 0, 100, 50], [[0, 0], [100, 50]], [[0, 0, 100, 50]]):
        r = Rectangle(box)
        # Как cv2.boundingRect: границы включительные
        assert (r.width, r.height) == (101, 51)
        assert r.coords == [[0, 51], [0, 0], [101, 0], [101, 51]]
        assert r.angle == 0 and not r.rotated
        assert r.area == 101 * 51
        assert (r.cp, r.lcp, r.rcp, r.tcp, r.bcp) == (
            Point(50, 26), Point(0, 26), Point(101, 26), Point(50, 0), Point(50, 51)
        )
        assert r.contour.shape == (4, 1, 2) and r.contour.dtype == np.int32


def test_requires_two_points() -> None:
    with pytest.raises(ValueError):
        Rectangle(np.array([[[1, 1]]], dtype=np.int32))
    with pytest.raises(ValueError):
        Rectangle([1, 2, 3])


def test_shift_updates_everything() -> None:
    r = Rectangle([0, 0, 100, 50])
    r.shift(Point(10, 20))
    assert r.coords == [[10, 71], [10, 20], [111, 20], [111, 71]]
    assert r.cp == Point(60, 46)
    assert r.tcp == Point(60, 20)
    assert r.contour.reshape(-1, 2).tolist() == r.coords


def test_decrease_axis_aligned() -> None:
    r = Rectangle([0, 0, 200, 100])
    d = r.decrease(10, 20)
    assert (d.width, d.height) == (161, 61)
    assert d.coords == [[20, 81], [20, 20], [181, 20], [181, 81]]
    assert r.width == 201  # исходный не меняется
    with pytest.raises(ValueError):
        r.decrease(60, 0)


def test_shift_given_angle_axis_aligned() -> None:
    r = Rectangle([0, 0, 100, 50]).shift_given_angle(10)
    assert r.coords == [[10, 51], [10, 0], [111, 0], [111, 51]]
    assert (r.width, r.height) == (101, 51)


def test_rotated_requires_cv2(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "cv2":
            raise ImportError("no cv2")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(ImportError, match=r"neuro-geometry\[cv\]"):
        Rectangle([0, 0, 10, 0, 10, 10], rotated=True)
