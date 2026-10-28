import pytest

from neuro_geometry import Line, LineDirection, Point


def test_horizontal_line() -> None:
    line = Line([[100, 10], [0, 0]])
    assert line.direction == LineDirection.HORIZONTAL
    assert (line.lp, line.rp, line.tp, line.bp) == (Point(0, 0), Point(100, 10), None, None)
    assert line.coords == [[0, 0], [100, 10]]
    assert line.cp == Point(50, 5)
    assert len(line) == line.length == 100
    assert line.list_of_tuples() == [(0, 0), (100, 10)]


def test_vertical_line() -> None:
    line = Line([[10, 100], [0, 0]])
    assert line.direction == LineDirection.VERTICAL
    assert (line.tp, line.bp, line.lp, line.rp) == (Point(0, 0), Point(10, 100), None, None)
    assert len(line) == 100
    assert line.list_of_tuples() == [(0, 0), (10, 100)]


def test_diagonal_45_is_horizontal() -> None:
    assert Line([[0, 0], [10, 10]]).direction == LineDirection.HORIZONTAL


def test_does_not_mutate_caller_coords() -> None:
    original = [[100, 50], [0, 50]]
    Line(original)
    assert original == [[100, 50], [0, 50]]


def test_requires_two_points() -> None:
    with pytest.raises(ValueError):
        Line([[0, 0]])


def test_x_and_y_on_line() -> None:
    line = Line([[0, 0], [10, 20]])
    assert line.get_x_on_line(Point(0, 10)) == 5
    assert line.get_y_on_line(Point(5, 0)) == 10
    assert Line([[0, 0], [100, 10]]).get_x_on_line(Point(0, 5)) == 50
    assert Line([[0, 0], [10, 100]]).get_y_on_line(Point(5, 0)) == 50
    assert Line([[5, 0], [5, 100]]).get_x_on_line(Point(0, 40)) == 5
    assert Line([[0, 7], [100, 7]]).get_y_on_line(Point(40, 0)) == 7


def test_x_y_on_line_undefined() -> None:
    with pytest.raises(ValueError):
        Line([[0, 7], [100, 7]]).get_x_on_line(Point(0, 0))
    with pytest.raises(ValueError):
        Line([[5, 0], [5, 100]]).get_y_on_line(Point(0, 0))


def test_intersection_with_line() -> None:
    a = Line([[0, 0], [10, 10]])
    assert a.get_intersection_point_with_line(Line([[0, 10], [10, 0]])) == Point(5, 5)
    assert a.get_intersection_point_with_line(Line([[100, 0], [110, 10]])) is None
    # Прямые, а не отрезки: пересечение за пределами отрезков
    assert a.get_intersection_point_with_line(Line([[20, 0], [20, 5]])) == Point(20, 20)


def test_intersection_with_segment() -> None:
    a = Line([[0, 0], [10, 10]])
    assert a.get_intersection_point_with_line_segment(Line([[0, 10], [10, 0]])) == Point(5, 5)
    assert a.get_intersection_point_with_line_segment(Line([[20, 0], [20, 5]])) is None
    assert a.get_intersection_point_with_line_segment((Point(0, 10), Point(10, 0))) == Point(5, 5)
    assert a.get_intersection_point_with_line_segment((Point(20, 0), Point(30, 5))) is None
    assert a.get_intersection_point_with_line_segment(Line([[1, 0], [11, 10]])) is None
