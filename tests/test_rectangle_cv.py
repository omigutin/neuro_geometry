""" Сверка Rectangle с OpenCV: выполняется только при установленном cv2. """

import numpy as np
import pytest

from neuro_geometry import Rectangle

cv2 = pytest.importorskip("cv2")


def _sorted(points: np.ndarray) -> np.ndarray:
    return points[np.lexsort((points[:, 1], points[:, 0]))]


def test_rotated_matches_min_area_rect() -> None:
    rng = np.random.default_rng(0)
    for _ in range(500):
        contour = rng.integers(0, 1920, size=(int(rng.integers(3, 30)), 1, 2)).astype(np.int32)
        r = Rectangle.from_points(contour, rotated=True)
        rect = cv2.minAreaRect(contour)
        assert r.area == pytest.approx(rect[1][0] * rect[1][1], rel=1e-6)
        assert -45 < r.angle <= 45
        # Та же геометрия, что у cv2.boxPoints (с точностью float32 OpenCV)
        assert np.allclose(_sorted(r.corners), _sorted(cv2.boxPoints(rect).astype(np.float64)), atol=1e-2)
        # Имена вершин соответствуют положению
        assert r.ltp.x < r.rtp.x and r.ltp.y < r.lbp.y


def test_axis_aligned_vs_bounding_rect() -> None:
    rng = np.random.default_rng(1)
    for _ in range(200):
        contour = rng.integers(0, 1000, size=(int(rng.integers(1, 20)), 1, 2)).astype(np.int32)
        x, y, w, h = cv2.boundingRect(contour)
        # Геометрическая ширина на 1 меньше пиксельной у OpenCV
        assert Rectangle.from_points(contour).bounding_box() == (x, y, x + w - 1, y + h - 1)
        assert Rectangle.from_xywh(x, y, w, h).bounding_box() == (x, y, x + w, y + h)


def test_points_inside_rotated() -> None:
    rng = np.random.default_rng(2)
    pts = rng.integers(0, 500, size=(40, 2)).astype(np.float64)
    r = Rectangle.from_points(pts, rotated=True)
    assert all(r.contains(__import__("neuro_geometry").Point(x, y), eps=1e-2) for x, y in pts)
