""" Отрезок из двух точек с определением преобладающего направления. """

from __future__ import annotations

__all__ = ["Line", "LineDirection"]

from collections.abc import Sequence
from enum import Enum

from .point import Point
from .types import Coords, CoordsLike


class LineDirection(Enum):
    """ Преобладающее направление отрезка. """

    NONE = 0
    VERTICAL = 1
    HORIZONTAL = 2


class Line:
    """
    Отрезок из двух точек.

    Направление: HORIZONTAL, если |dx| >= |dy| (угол наклона <= 45°), иначе VERTICAL.
    Для вертикального отрезка заполнены tp/bp (верхняя/нижняя точки), lp/rp = None.
    Для горизонтального заполнены lp/rp (левая/правая точки), tp/bp = None.
    coords — копия входных точек, упорядоченная так же (tp, bp) или (lp, rp).
    """

    def __init__(self, coords: CoordsLike) -> None:
        if len(coords) != 2:
            raise ValueError(f"Line requires exactly 2 points, got {len(coords)}")

        # Копия точек: не мутировать список вызывающего кода
        pts: Coords = [list(coords[0]), list(coords[1])]
        delta_x = abs(pts[0][0] - pts[1][0])
        delta_y = abs(pts[0][1] - pts[1][1])

        self.direction: LineDirection = LineDirection.HORIZONTAL if delta_y <= delta_x else LineDirection.VERTICAL
        self.tp: Point | None = None
        self.bp: Point | None = None
        self.lp: Point | None = None
        self.rp: Point | None = None

        if self.direction == LineDirection.VERTICAL:
            pts.sort(key=lambda p: p[1])
            first, second = Point(pts[0]), Point(pts[1])
            self.tp, self.bp = first, second
        else:
            pts.sort(key=lambda p: p[0])
            first, second = Point(pts[0]), Point(pts[1])
            self.lp, self.rp = first, second

        self.coords: Coords = pts
        self.cp: Point = Point((first.x + second.x) / 2, (first.y + second.y) / 2)
        self.length: int = first.distance_to(second)

    @property
    def _ends(self) -> tuple[Point, Point]:
        """ Концы отрезка в порядке coords: (tp, bp) или (lp, rp). """
        return Point(self.coords[0]), Point(self.coords[1])

    def get_x_on_line(self, point: Point) -> float:
        """ X прямой, проходящей через отрезок, при y = point.y. """
        (x1, y1), (x2, y2) = self.coords
        if y1 == y2:
            raise ValueError("Line is horizontal: X is undefined for a given Y")
        return x1 + (point.y - y1) * (x2 - x1) / (y2 - y1)

    def get_y_on_line(self, point: Point) -> float:
        """ Y прямой, проходящей через отрезок, при x = point.x. """
        (x1, y1), (x2, y2) = self.coords
        if x1 == x2:
            raise ValueError("Line is vertical: Y is undefined for a given X")
        return y1 + (point.x - x1) * (y2 - y1) / (x2 - x1)

    def list_of_tuples(self) -> list[tuple[int, int]]:
        """ Концы отрезка списком кортежей: [(tp), (bp)] или [(lp), (rp)]. """
        first, second = self._ends
        return [first.tuple(), second.tuple()]

    def get_intersection_point_with_line(self, line2: Line) -> Point | None:
        """ Точка пересечения прямых, проходящих через отрезки; None, если прямые параллельны. """
        (x1, y1), (x2, y2) = self.coords
        (x3, y3), (x4, y4) = line2.coords

        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denominator == 0:
            return None
        a = x1 * y2 - y1 * x2
        b = x3 * y4 - y3 * x4
        return Point((a * (x3 - x4) - (x1 - x2) * b) / denominator, (a * (y3 - y4) - (y1 - y2) * b) / denominator)

    def get_intersection_point_with_line_segment(self, line_or_points: Line | Sequence[Point]) -> Point | None:
        """
        Точка пересечения двух отрезков; None, если отрезки не пересекаются или параллельны.
        Аргумент — другой Line либо пара точек (начало, конец).
        """
        if isinstance(line_or_points, Line):
            (p1x, p1y), (p2x, p2y) = self.coords
            (p3x, p3y), (p4x, p4y) = line_or_points.coords
        else:
            start, end = line_or_points
            p1x, p1y, p2x, p2y = start.x, start.y, end.x, end.y
            (p3x, p3y), (p4x, p4y) = self.coords

        d1x, d1y = p2x - p1x, p2y - p1y
        d2x, d2y = p4x - p3x, p4y - p3y
        denominator = d1x * d2y - d1y * d2x
        if denominator == 0:
            return None
        t = ((p3x - p1x) * d2y - (p3y - p1y) * d2x) / denominator
        u = ((p3x - p1x) * d1y - (p3y - p1y) * d1x) / denominator
        if 0 <= t <= 1 and 0 <= u <= 1:
            return Point(p1x + t * d1x, p1y + t * d1y)
        return None

    def __len__(self) -> int:
        """ Длина отрезка, округлённая до int. """
        return self.length
