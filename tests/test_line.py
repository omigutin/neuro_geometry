import pytest

from neuro_geometry import Line, LineDirection, Point


def test_constructors_and_order_preserved() -> None:
    line = Line.from_coords([[100, 10], [0, 0]])
    assert line == Line(100, 10, 0, 0) == Line.from_points(Point(100, 10), Point(0, 0))
    assert line.start == Point(100, 10) and line.end == Point(0, 0)
    assert line.to_coords() == [[100.0, 10.0], [0.0, 0.0]]
    with pytest.raises(ValueError):
        Line.from_coords([[0, 0]])


def test_positional_ends_always_defined() -> None:
    h = Line(100, 10, 0, 0)
    assert h.direction == LineDirection.HORIZONTAL
    assert (h.lp, h.rp, h.tp, h.bp) == (Point(0, 0), Point(100, 10), Point(0, 0), Point(100, 10))
    v = Line(10, 0, 0, 100)
    assert v.direction == LineDirection.VERTICAL
    assert (v.tp, v.bp, v.lp, v.rp) == (Point(10, 0), Point(0, 100), Point(0, 100), Point(10, 0))
    assert Line(0, 0, 10, 10).direction == LineDirection.HORIZONTAL
    assert Line(1, 1, 1, 1).direction == LineDirection.NONE


def test_metrics() -> None:
    line = Line(0, 0, 3, 4)
    assert line.length == 5.0
    assert line.center == Point(1.5, 2)
    assert (line.dx, line.dy) == (3, 4)
    assert Line(0, 0, 0, 10).angle == 90.0


def test_x_at_y_at() -> None:
    line = Line(0, 0, 10, 20)
    assert line.x_at(10) == 5 and line.y_at(5) == 10
    assert Line(5, 0, 5, 100).x_at(40) == 5
    assert Line(0, 7, 100, 7).y_at(40) == 7
    with pytest.raises(ValueError):
        Line(0, 7, 100, 7).x_at(0)
    with pytest.raises(ValueError):
        Line(5, 0, 5, 100).y_at(0)


def test_side_of_and_distance() -> None:
    line = Line(0, 0, 10, 0)  # направление вправо; ось Y вниз
    assert line.side_of(Point(5, 5)) > 0  # ниже на изображении = справа по ходу
    assert line.side_of(Point(5, -5)) < 0
    assert line.side_of(Point(20, 0)) == 0
    assert line.distance_to_point(Point(5, 3)) == 3
    assert line.distance_to_point(Point(13, 4)) == 5
    assert Line(1, 1, 1, 1).distance_to_point(Point(4, 5)) == 5


def test_intersections() -> None:
    a = Line(0, 0, 10, 10)
    assert a.intersection_with_line(Line(0, 10, 10, 0)) == Point(5, 5)
    assert a.intersection_with_line(Line(100, 0, 110, 10)) is None
    assert a.intersection_with_line(Line(20, 0, 20, 5)) == Point(20, 20)
    assert a.intersection_with_segment(Line(0, 10, 10, 0)) == Point(5, 5)
    assert a.intersection_with_segment(Line(20, 0, 20, 5)) is None
    assert a.intersection_with_segment(Line(10, 10, 20, 0)) == Point(10, 10)  # касание концом
    # Точность: без округления до пикселей
    assert Line(0, 0, 3, 1).intersection_with_line(Line(0, 1, 3, 0)) == Point(1.5, 0.5)


def test_inplace_vs_new() -> None:
    line = Line(0, 0, 10, 0)
    moved = line.shifted(1, 2)
    assert line == Line(0, 0, 10, 0) and moved == Line(1, 2, 11, 2)
    line_id = id(line)
    line.shift(1, 2)
    assert id(line) == line_id and line == moved
    line.set(0, 0, 1, 1)
    line.x2 = 5
    assert line == Line(0, 0, 5, 1)
    copy = line.copy()
    copy.shift(1, 1)
    assert line == Line(0, 0, 5, 1)
