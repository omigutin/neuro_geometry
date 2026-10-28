import pytest

from neuro_geometry import Point


def test_float_storage_and_constructors() -> None:
    p = Point(1, 2.5)
    assert (p.x, p.y) == (1.0, 2.5) and isinstance(p.x, float)
    assert Point.from_seq([3, 4]) == Point(3, 4)
    with pytest.raises(ValueError):
        Point.from_seq([1, 2, 3])


def test_inplace_vs_new() -> None:
    p = Point(1, 2)
    q = p.shifted(10, 20)
    assert p == Point(1, 2) and q == Point(11, 22)

    p_id = id(p)
    p.shift(1, 1)
    p += Point(1, 1)
    p -= Point(0, 2)
    assert id(p) == p_id and p == Point(3, 2)
    p.set(0, 0)
    assert p == Point(0, 0)

    c = q.copy()
    c.shift(1, 1)
    assert q == Point(11, 22)


def test_arithmetic() -> None:
    assert Point(1, 2) + Point(3, 4) == Point(4, 6)
    assert Point(3, 4) - Point(1, 2) == Point(2, 2)
    assert Point(1, 2) * 2 == 2 * Point(1, 2) == Point(2, 4)
    assert -Point(1, -2) == Point(-1, 2)
    x, y = Point(5, 6)
    assert (x, y) == (5.0, 6.0)


def test_distance_and_conversions() -> None:
    assert Point(0, 0).distance_to(Point(3, 4)) == 5.0
    assert Point(0, 0).distance_to(Point(1, 1)) == pytest.approx(2**0.5)
    assert Point(2.5, -2.5).to_int_tuple() == (3, -2)
    assert Point(1.5, 2).to_tuple() == (1.5, 2.0)
    assert Point(1.5, 2).to_list() == [1.5, 2.0]
    assert Point(0.1 + 0.2, 0).isclose(Point(0.3, 0))


def test_not_hashable() -> None:
    with pytest.raises(TypeError):
        hash(Point(1, 2))
    assert repr(Point(1, 2.5)) == "Point(1, 2.5)"
