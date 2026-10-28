import pytest

from neuro_geometry import Point, Triangle


def test_metrics() -> None:
    t = Triangle(Point(0, 40), Point(0, 0), Point(30, 40))
    assert (t.ab, t.bc, t.ca) == (40, 50, 30)
    assert t.perimeter == 120 and t.area == 600
    assert t.centroid == Point(10, 80 / 3)
    assert t.a == Point(0, 40) and t.coords == [[0, 40], [0, 0], [30, 40]]
    assert Triangle.from_coords(t.coords) == t
    with pytest.raises(ValueError):
        Triangle.from_coords([[0, 0], [1, 1]])


def test_inplace_vs_new() -> None:
    t = Triangle(Point(0, 0), Point(1, 0), Point(0, 1))
    s = t.shifted(1, 1)
    assert t.a == Point(0, 0) and s.a == Point(1, 1)
    t_id = id(t)
    t.shift(1, 1)
    assert t == s and id(t) == t_id
