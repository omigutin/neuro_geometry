""" Точка на плоскости изображения. """

from __future__ import annotations

import math
from collections.abc import Iterator, Sequence

from ._rounding import round_half_up


class Point:
    """
    Изменяемая точка с координатами float. Ось Y направлена вниз (координаты изображения).

    Изменение на месте: shift(), set(), операторы += и -=.
    Новый объект: shifted(), copy(), операторы +, -, *.
    Точка изменяемая, поэтому не хешируется (её нельзя класть в set или использовать как ключ dict).
    """

    __slots__ = ("x", "y")

    x: float
    y: float

    def __init__(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)

    @classmethod
    def from_seq(cls, xy: Sequence[float]) -> Point:
        """ Точка из пары [x, y] / (x, y). """
        if len(xy) != 2:
            raise ValueError(f"Point requires 2 coordinates, got {len(xy)}")
        return cls(xy[0], xy[1])

    def copy(self) -> Point:
        """ Независимая копия. """
        return Point(self.x, self.y)

    def set(self, x: float, y: float) -> None:
        """ Задаёт координаты на месте. """
        self.x = float(x)
        self.y = float(y)

    def shift(self, dx: float, dy: float) -> None:
        """ Сдвигает точку на месте. """
        self.x += dx
        self.y += dy

    def shifted(self, dx: float, dy: float) -> Point:
        """ Новая точка, сдвинутая на (dx, dy). """
        return Point(self.x + dx, self.y + dy)

    def distance_to(self, other: Point) -> float:
        """ Евклидово расстояние. """
        return math.hypot(self.x - other.x, self.y - other.y)

    def isclose(self, other: Point, abs_tol: float = 1e-9) -> bool:
        """ Совпадение координат с допуском. """
        return abs(self.x - other.x) <= abs_tol and abs(self.y - other.y) <= abs_tol

    def to_tuple(self) -> tuple[float, float]:
        """ (x, y) """
        return self.x, self.y

    def to_int_tuple(self) -> tuple[int, int]:
        """ (x, y) в пикселях, округление половины вверх — для функций OpenCV. """
        return round_half_up(self.x), round_half_up(self.y)

    def to_list(self) -> list[float]:
        """ [x, y] """
        return [self.x, self.y]

    def __add__(self, other: Point) -> Point:
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Point) -> Point:
        return Point(self.x - other.x, self.y - other.y)

    def __iadd__(self, other: Point) -> Point:
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other: Point) -> Point:
        self.x -= other.x
        self.y -= other.y
        return self

    def __mul__(self, k: float) -> Point:
        return Point(self.x * k, self.y * k)

    __rmul__ = __mul__

    def __neg__(self) -> Point:
        return Point(-self.x, -self.y)

    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    __hash__ = None  # type: ignore[assignment]

    def __repr__(self) -> str:
        return f"Point({self.x:g}, {self.y:g})"
