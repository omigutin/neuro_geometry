import pytest

from neuro_geometry import Point, Quadrangle


@pytest.mark.parametrize(
    "coords", [[[0, 0], [10, 20]], [[10, 20], [0, 0]], [[0, 20], [10, 0]], [[10, 0], [0, 20]]]
)
def test_from_two_points(coords: list) -> None:
    q = Quadrangle(coords)
    assert q.coords == [[0, 20], [0, 0], [10, 0], [10, 20]]
    assert (q.min_width, q.max_width, q.min_height, q.max_height) == (10, 10, 20, 20)
    assert q.area == 200
    assert q.cp == Point(5, 10)


def test_from_four_points_any_order() -> None:
    q = Quadrangle([[100, 0], [0, 50], [60, 50], [0, 0]])
    assert (q.lbp, q.ltp, q.rtp, q.rbp) == (Point(0, 50), Point(0, 0), Point(100, 0), Point(60, 50))
    assert (q.top_width, q.bottom_width, q.left_height, q.right_height) == (100, 60, 50, 64)
    assert q.area == 4000  # трапеция


def test_area_non_cyclic() -> None:
    assert Quadrangle([[0, 0], [100, 0], [100, 50], [0, 100]]).area == 7500


def test_one_pixel_quadrangle() -> None:
    q = Quadrangle([[0, 0], [0, 1], [1, 1], [1, 0]])
    assert q.coords == [[0, 1], [0, 0], [1, 0], [1, 1]]


def test_degenerate_raises() -> None:
    with pytest.raises(ValueError):
        Quadrangle([[5, 0], [5, 1], [5, 2], [5, 3]])
    with pytest.raises(ValueError):
        Quadrangle([[5, 0]])


def test_increase_decrease_shift() -> None:
    q = Quadrangle([[0, 0], [100, 50]])
    assert q.get_decreased_coords(10, 10) == [[10, 45], [10, 5], [90, 5], [90, 45]]
    assert q.get_increased_coords(10, 10) == [[-10, 55], [-10, -5], [110, -5], [110, 55]]
    q.shift(Point(1, 2))
    assert q.coords == [[1, 52], [1, 2], [101, 2], [101, 52]]
    q.decrease(10, 10)
    assert q.coords == [[11, 47], [11, 7], [91, 7], [91, 47]]
    q.increase(0, 0)
    assert q.coords == [[11, 47], [11, 7], [91, 7], [91, 47]]


def test_side_centers() -> None:
    q = Quadrangle([[0, 0], [100, 10], [100, 60], [0, 50]])
    assert q.tcp == Point(50, 5)
    assert q.bcp == Point(50, 55)
