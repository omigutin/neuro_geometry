import builtins
from typing import Any

import pytest

from neuro_geometry import Point, Rectangle


def test_constructors() -> None:
    r = Rectangle.from_box(100, 50, 0, 0)
    assert r == Rectangle(50, 25, 100, 50) == Rectangle.from_xywh(0, 0, 100, 50)
    assert Rectangle.from_points([[0, 0], [100, 50], [30, 10]]) == r
    assert Rectangle.from_points([[[0, 0]], [[100, 50]]]) == r
    with pytest.raises(ValueError):
        Rectangle(0, 0, -1, 1)
    with pytest.raises(ValueError):
        Rectangle.from_points([])


def test_axis_aligned_geometry() -> None:
    r = Rectangle.from_box(0, 0, 100, 50)
    assert (r.width, r.height, r.area, r.angle) == (100, 50, 5000, 0)
    assert r.is_axis_aligned
    assert r.coords == [[0, 50], [0, 0], [100, 0], [100, 50]]
    assert (r.lbp, r.ltp, r.rtp, r.rbp) == (Point(0, 50), Point(0, 0), Point(100, 0), Point(100, 50))
    assert (r.cp, r.lcp, r.rcp, r.tcp, r.bcp) == (
        Point(50, 25), Point(0, 25), Point(100, 25), Point(50, 0), Point(50, 50)
    )
    assert r.bounding_box() == (0, 0, 100, 50)
    assert Rectangle.from_box(0.4, 0.5, 10.5, 9.6).to_int_box() == (0, 1, 11, 10)
    assert r.contour.reshape(-1, 2).tolist() == r.coords


def test_rotated_geometry_without_cv2() -> None:
    r = Rectangle(0, 0, 4, 2, angle=90)  # нормализуется: угол 0, стороны меняются местами
    assert (r.width, r.height, r.angle) == (2, 4, 0)
    r = Rectangle(0, 0, 4, 2, angle=30)
    assert r.area == 8
    assert r.ltp.distance_to(r.rtp) == pytest.approx(4)
    assert r.ltp.distance_to(r.lbp) == pytest.approx(2)
    assert r.tcp.isclose(Point((r.ltp.x + r.rtp.x) / 2, (r.ltp.y + r.rtp.y) / 2))
    assert r.ltp.y < r.lbp.y and r.ltp.x < r.rtp.x
    assert r.contains(Point(0, 0)) and r.contains(r.rbp) and not r.contains(Point(2, 2))


def test_inplace_does_not_reallocate() -> None:
    r = Rectangle.from_box(0, 0, 100, 50)
    corners_buffer = r.corners.base
    rect_id = id(r)
    r.shift(10, 5)
    assert id(r) == rect_id and r.corners.base is corners_buffer
    assert r.coords == [[10, 55], [10, 5], [110, 5], [110, 55]]
    assert r.contour.reshape(-1, 2).tolist() == r.coords


def test_inplace_vs_new() -> None:
    r = Rectangle.from_box(0, 0, 100, 50)
    assert r.shifted(1, 2) == Rectangle.from_box(1, 2, 101, 52)
    assert r.decreased(10, 20) == Rectangle(50, 25, 80, 30)
    assert r.increased(10) == Rectangle(50, 25, 120, 60)
    assert r.scaled(2, 0.5) == Rectangle(50, 25, 200, 25)
    assert r == Rectangle.from_box(0, 0, 100, 50)  # исходный не изменился

    r.decrease(10, 20)
    assert r == Rectangle(50, 25, 80, 30)
    r.increase(0)
    r.scale(1)
    assert r == Rectangle(50, 25, 80, 30)
    r.set_center(0, 0)
    r.width = 10
    r.height = 20
    assert r == Rectangle(0, 0, 10, 20)
    with pytest.raises(ValueError):
        r.decrease(51)
    with pytest.raises(ValueError):
        r.width = -1


def test_shift_along_axes() -> None:
    r = Rectangle(0, 0, 10, 4, angle=30)
    s = r.shifted_along_axes(10)
    assert s.cp.isclose(Point(10 * 0.8660254037844387, 5))
    assert (s.width, s.height, s.angle) == (r.width, r.height, r.angle)
    r.shift_along_axes(0, 2)
    assert r.cp.isclose(Point(-1, 2 * 0.8660254037844387))


def test_copy_is_independent() -> None:
    r = Rectangle.from_box(0, 0, 10, 10)
    c = r.copy()
    c.shift(5, 5)
    assert r == Rectangle.from_box(0, 0, 10, 10)


def test_corners_readonly() -> None:
    r = Rectangle.from_box(0, 0, 10, 10)
    with pytest.raises(ValueError):
        r.corners[0, 0] = 5
    with pytest.raises(ValueError):
        r.contour[0, 0, 0] = 5


def test_rotated_requires_cv2(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "cv2":
            raise ImportError("no cv2")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(ImportError, match=r"neuro-geometry\[cv\]"):
        Rectangle.from_points([[0, 0], [10, 0], [10, 10]], rotated=True)
