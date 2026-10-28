import pytest

from neuro_geometry import Point


@pytest.mark.parametrize("args", [(1, 2), ((1, 2),), ([1, 2],), (1.2, 1.8), ("1", "2")])
def test_constructor_forms(args: tuple) -> None:
    assert Point(*args).tuple() == (1, 2)


def test_float_rounding_is_python_round() -> None:
    assert Point(1.5, 2.5).tuple() == (2, 2)


@pytest.mark.parametrize(
    ("args", "exc"),
    [((3,), TypeError), (((1, 2), 3), TypeError), (((1, 2, 3),), ValueError), (("a", 1), TypeError)],
)
def test_invalid_args(args: tuple, exc: type[Exception]) -> None:
    with pytest.raises(exc):
        Point(*args)


def test_arithmetic_and_distance() -> None:
    a, b = Point(1, 2), Point(4, 6)
    assert a + b == Point(5, 8)
    assert b - a == Point(3, 4)
    assert a.distance_to(b) == 5


def test_equality_hash_repr() -> None:
    assert Point(1, 2) == Point(1, 2)
    assert Point(1, 2) != Point(2, 1)
    assert len({Point(1, 2), Point(1, 2)}) == 1
    assert repr(Point(1, 2)) == "Point(1, 2)"
    assert Point(1, 2).list() == [1, 2]


def test_numpy_scalars() -> None:
    np = pytest.importorskip("numpy")
    assert Point(np.float32(1.6), np.int64(2)).tuple() == (2, 2)
    assert Point(np.float64(-1.6), np.int32(-2)).tuple() == (-2, -2)
