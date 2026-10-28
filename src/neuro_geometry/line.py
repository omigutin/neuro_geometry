""" Отрезок на плоскости изображения. """

from __future__ import annotations

__all__ = ["Line", "LineDirection"]

import math
from enum import Enum

from .point import Point
from .types import Coords, CoordsLike

# Допуск для проверки «точка на отрезке» при float-вычислениях параметров t, u
_SEGMENT_EPS = 1e-9


class LineDirection(Enum):
    """ Преобладающее направление отрезка. """

    NONE = 0
    VERTICAL = 1
    HORIZONTAL = 2


class Line:
    """
    Отрезок start -> end. Порядок концов сохраняется таким, как передан.

    Направление: HORIZONTAL, если |dx| >= |dy|, VERTICAL — иначе, NONE — для отрезка нулевой длины.
    Концы по положению (tp, bp, lp, rp) доступны всегда, независимо от направления.
    Изменение на месте: shift(), set(), прямое присваивание x1, y1, x2, y2.
    Новый объект: shifted(), copy().
    """

    __slots__ = ("x1", "x2", "y1", "y2")

    x1: float
    y1: float
    x2: float
    y2: float

    def __init__(self, x1: float, y1: float, x2: float, y2: float) -> None:
        self.x1, self.y1, self.x2, self.y2 = float(x1), float(y1), float(x2), float(y2)

    @classmethod
    def from_points(cls, start: Point, end: Point) -> Line:
        """ Отрезок из двух точек. """
        return cls(start.x, start.y, end.x, end.y)

    @classmethod
    def from_coords(cls, coords: CoordsLike) -> Line:
        """ Отрезок из [[x1, y1], [x2, y2]]. """
        if len(coords) != 2:
            raise ValueError(f"Line requires exactly 2 points, got {len(coords)}")
        (x1, y1), (x2, y2) = coords
        return cls(x1, y1, x2, y2)

    def copy(self) -> Line:
        """ Независимая копия. """
        return Line(self.x1, self.y1, self.x2, self.y2)

    def set(self, x1: float, y1: float, x2: float, y2: float) -> None:
        """ Задаёт концы на месте. """
        self.x1, self.y1, self.x2, self.y2 = float(x1), float(y1), float(x2), float(y2)

    def shift(self, dx: float, dy: float) -> None:
        """ Сдвигает отрезок на месте. """
        self.x1 += dx
        self.x2 += dx
        self.y1 += dy
        self.y2 += dy

    def shifted(self, dx: float, dy: float) -> Line:
        """ Новый отрезок, сдвинутый на (dx, dy). """
        return Line(self.x1 + dx, self.y1 + dy, self.x2 + dx, self.y2 + dy)

    @property
    def start(self) -> Point:
        return Point(self.x1, self.y1)

    @property
    def end(self) -> Point:
        return Point(self.x2, self.y2)

    @property
    def dx(self) -> float:
        return self.x2 - self.x1

    @property
    def dy(self) -> float:
        return self.y2 - self.y1

    @property
    def length(self) -> float:
        return math.hypot(self.x2 - self.x1, self.y2 - self.y1)

    @property
    def angle(self) -> float:
        """ Угол направления start -> end в градусах, (-180, 180]; ось Y вниз, поэтому положительный — по часовой. """
        return math.degrees(math.atan2(self.y2 - self.y1, self.x2 - self.x1))

    @property
    def direction(self) -> LineDirection:
        adx, ady = abs(self.x2 - self.x1), abs(self.y2 - self.y1)
        if adx == 0 and ady == 0:
            return LineDirection.NONE
        return LineDirection.HORIZONTAL if ady <= adx else LineDirection.VERTICAL

    @property
    def center(self) -> Point:
        return Point((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)

    @property
    def tp(self) -> Point:
        """ Верхний конец (меньший Y; при равенстве — start). """
        return self.start if self.y1 <= self.y2 else self.end

    @property
    def bp(self) -> Point:
        """ Нижний конец (больший Y; при равенстве — end). """
        return self.end if self.y1 <= self.y2 else self.start

    @property
    def lp(self) -> Point:
        """ Левый конец (меньший X; при равенстве — start). """
        return self.start if self.x1 <= self.x2 else self.end

    @property
    def rp(self) -> Point:
        """ Правый конец (больший X; при равенстве — end). """
        return self.end if self.x1 <= self.x2 else self.start

    def to_coords(self) -> Coords:
        """ [[x1, y1], [x2, y2]] """
        return [[self.x1, self.y1], [self.x2, self.y2]]

    def x_at(self, y: float) -> float:
        """ X прямой, проходящей через отрезок, при заданном Y. """
        if self.y1 == self.y2:
            raise ValueError("Line is horizontal: X is undefined for a given Y")
        return self.x1 + (y - self.y1) * (self.x2 - self.x1) / (self.y2 - self.y1)

    def y_at(self, x: float) -> float:
        """ Y прямой, проходящей через отрезок, при заданном X. """
        if self.x1 == self.x2:
            raise ValueError("Line is vertical: Y is undefined for a given X")
        return self.y1 + (x - self.x1) * (self.y2 - self.y1) / (self.x2 - self.x1)

    def side_of(self, point: Point) -> float:
        """
        Векторное произведение (end - start) x (point - start).
        > 0 — точка справа от направления start -> end (на изображении), < 0 — слева, 0 — на прямой.
        """
        return (self.x2 - self.x1) * (point.y - self.y1) - (self.y2 - self.y1) * (point.x - self.x1)

    def distance_to_point(self, point: Point) -> float:
        """ Расстояние от точки до отрезка. """
        dx, dy = self.x2 - self.x1, self.y2 - self.y1
        length_sq = dx * dx + dy * dy
        if length_sq == 0:
            return math.hypot(point.x - self.x1, point.y - self.y1)
        t = max(0.0, min(1.0, ((point.x - self.x1) * dx + (point.y - self.y1) * dy) / length_sq))
        return math.hypot(point.x - (self.x1 + t * dx), point.y - (self.y1 + t * dy))

    def _intersection_params(self, other: Line) -> tuple[float, float] | None:
        """ Параметры t (на self) и u (на other) точки пересечения прямых; None для параллельных. """
        d1x, d1y = self.x2 - self.x1, self.y2 - self.y1
        d2x, d2y = other.x2 - other.x1, other.y2 - other.y1
        denominator = d1x * d2y - d1y * d2x
        if denominator == 0:
            return None
        ox, oy = other.x1 - self.x1, other.y1 - self.y1
        return (ox * d2y - oy * d2x) / denominator, (ox * d1y - oy * d1x) / denominator

    def intersection_with_line(self, other: Line) -> Point | None:
        """ Точка пересечения прямых, проходящих через отрезки; None, если прямые параллельны. """
        params = self._intersection_params(other)
        if params is None:
            return None
        t = params[0]
        return Point(self.x1 + t * (self.x2 - self.x1), self.y1 + t * (self.y2 - self.y1))

    def intersection_with_segment(self, other: Line) -> Point | None:
        """ Точка пересечения отрезков (концы включительно); None, если не пересекаются или параллельны. """
        params = self._intersection_params(other)
        if params is None:
            return None
        t, u = params
        if -_SEGMENT_EPS <= t <= 1 + _SEGMENT_EPS and -_SEGMENT_EPS <= u <= 1 + _SEGMENT_EPS:
            return Point(self.x1 + t * (self.x2 - self.x1), self.y1 + t * (self.y2 - self.y1))
        return None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Line):
            return NotImplemented
        return (self.x1, self.y1, self.x2, self.y2) == (other.x1, other.y1, other.x2, other.y2)

    __hash__ = None  # type: ignore[assignment]

    def __repr__(self) -> str:
        return f"Line(({self.x1:g}, {self.y1:g}) -> ({self.x2:g}, {self.y2:g}))"
