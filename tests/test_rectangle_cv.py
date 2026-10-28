""" Сверка Rectangle с OpenCV: выполняется только при установленном cv2. """

import math

import numpy as np
import pytest

from neuro_geometry import Point, Rectangle

cv2 = pytest.importorskip("cv2")


def _reference(contour: np.ndarray) -> tuple[list[list[int]], int, int, float]:
    """ Поведение pc_geometric_shapes.Rectangle(rotated=True) из production_counters. """
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    (_, _), (w, h), angle = rect
    width, height = (round(h), round(w)) if angle > 45 or angle < -45 else (round(w), round(h))
    return [[round(float(x)), round(float(y))] for x, y in box], width, height, angle


def test_rotated_matches_opencv() -> None:
    rng = np.random.default_rng(0)
    for _ in range(300):
        contour = rng.integers(0, 1920, size=(int(rng.integers(3, 30)), 1, 2)).astype(np.int32)
        r = Rectangle(contour, rotated=True)
        coords, width, height, angle = _reference(contour)
        assert r.coords == coords
        assert (r.width, r.height) == (width, height)
        assert r.angle == pytest.approx(angle)


def test_rotated_accepts_int64_and_float() -> None:
    pts = np.array([[10, 10], [110, 40], [100, 80], [0, 50]])
    assert Rectangle(pts, True).coords == Rectangle(pts.astype(np.float64), True).coords


def test_axis_aligned_matches_bounding_rect() -> None:
    rng = np.random.default_rng(1)
    for _ in range(300):
        contour = rng.integers(0, 1000, size=(int(rng.integers(2, 20)), 1, 2)).astype(np.int32)
        x, y, w, h = cv2.boundingRect(contour)
        r = Rectangle(contour)
        assert (r.ltp.tuple(), r.width, r.height) == ((x, y), w, h)


def test_rotated_decrease_keeps_center_and_angle() -> None:
    contour = cv2.boxPoints(((500.0, 300.0), (200.0, 100.0), 30.0)).astype(np.int32)
    r = Rectangle(contour, rotated=True)
    d = r.decrease(10, 10)
    assert d.rotated and d.angle == r.angle and d.cp == r.cp
    assert (d.width, d.height) == (round(r.width * 0.8), round(r.height * 0.8))
    sides = sorted(Point(*a).distance_to(Point(*b)) for a, b in zip(d.coords, d.coords[1:] + d.coords[:1], strict=True))
    assert sides[0] == pytest.approx(min(d.width, d.height), abs=2)
    assert sides[-1] == pytest.approx(max(d.width, d.height), abs=2)


def test_rotated_shift_given_angle_is_parallel_translation() -> None:
    contour = cv2.boxPoints(((500.0, 300.0), (200.0, 100.0), 30.0)).astype(np.int32)
    r = Rectangle(contour, rotated=True)
    s = r.shift_given_angle(20)
    rad = math.radians(r.angle)
    vector = (20 * math.cos(rad), 20 * math.sin(rad)) if r.angle < 45 else (20 * math.sin(rad), -20 * math.cos(rad))
    expected = Point(*vector)
    assert all(Point(*b) - Point(*a) == expected for a, b in zip(r.coords, s.coords, strict=True))
    assert (s.width, s.height, s.angle) == (r.width, r.height, r.angle)
