import itertools

import numpy as np
import pytest

from neuro_geometry import Point, Quadrangle

TRAPEZOID = [[0, 50], [0, 0], [100, 0], [60, 50]]  # lbp, ltp, rtp, rbp


@pytest.mark.parametrize("perm", list(itertools.permutations(TRAPEZOID)))
def test_vertex_order_independent(perm: tuple) -> None:
    assert Quadrangle(list(perm)).coords == TRAPEZOID


def test_metrics() -> None:
    q = Quadrangle(TRAPEZOID)
    assert q.area == 4000
    assert (q.top_width, q.bottom_width, q.left_height) == (100, 60, 50)
    assert q.right_height == pytest.approx(64.03, abs=0.01)
    assert (q.min_width, q.max_width) == (60, 100)
    assert q.cp == Point(40, 25)
    assert (q.tcp, q.bcp, q.lcp) == (Point(50, 0), Point(30, 50), Point(0, 25))
    assert Quadrangle([[0, 0], [100, 0], [100, 50], [0, 100]]).area == 7500


def test_rotated_square_corners() -> None:
    # Квадрат, повёрнутый на 30°: каждая вершина ровно одна, ltp — самая «левая-верхняя»
    angle = np.radians(30)
    base = np.array([[-1, 1], [-1, -1], [1, -1], [1, 1]]) * 50
    rot = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    pts = base @ rot.T + 200
    q = Quadrangle(pts[[2, 0, 3, 1]])
    assert np.allclose(q.corners, pts)


def test_diamond_not_degenerate() -> None:
    q = Quadrangle([[50, 0], [100, 50], [50, 100], [0, 50]])
    assert len({tuple(c) for c in q.coords}) == 4
    assert q.area == 5000


def test_from_box_and_points() -> None:
    assert Quadrangle.from_box(10, 20, 0, 0).coords == [[0, 20], [0, 0], [10, 0], [10, 20]]
    cloud = [[0, 0], [5, 1], [100, 0], [50, 20], [100, 50], [0, 50], [10, 10]]
    assert Quadrangle.from_points(cloud).coords == [[0, 50], [0, 0], [100, 0], [100, 50]]
    with pytest.raises(ValueError):
        Quadrangle([[0, 0], [1, 1], [2, 2]])


def test_inplace_vs_new() -> None:
    q = Quadrangle.from_box(0, 0, 100, 50)
    q_id = id(q)
    shifted = q.shifted(1, 2)
    assert q.ltp == Point(0, 0) and shifted.ltp == Point(1, 2)
    q.shift(1, 2)
    assert q == shifted and id(q) == q_id
    smaller = q.decreased(10, 20)
    assert smaller.coords == [[11, 42], [11, 12], [91, 12], [91, 42]]
    assert q.coords == [[1, 52], [1, 2], [101, 2], [101, 52]]
    q.decrease(10, 20)
    assert q == smaller and id(q) == q_id
    assert q.increased(0).coords == q.coords
    with pytest.raises(ValueError):
        q.decrease(60)


def test_corners_copy_and_contour() -> None:
    q = Quadrangle.from_box(0, 0, 10.5, 5)
    q.corners[0, 0] = 100
    q.coords[0][0] = 100
    assert q.lbp == Point(0, 5)
    assert q.contour.reshape(-1, 2).tolist() == [[0, 5], [0, 0], [11, 0], [11, 5]]
