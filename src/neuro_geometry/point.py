""" Точка с целочисленными координатами. """

from __future__ import annotations

import builtins
from collections.abc import Sequence
from math import sqrt
from numbers import Integral, Real
from typing import SupportsInt, TypeAlias

# float, int, numpy-скаляры и всё, что приводится через int()
Number: TypeAlias = SupportsInt


class Point:
    """ Точка на изображении: координаты приводятся к int (дробные округляются через round(), остальные — int()). """

    __slots__ = ("x", "y")

    x: int
    y: int

    def __init__(self, x: Number | Sequence[Number], y: Number | None = None) -> None:
        if isinstance(x, (list, tuple)):
            if y is not None:
                raise TypeError("Point: 'y' must be omitted when 'x' is a sequence")
            if len(x) != 2:
                raise ValueError(f"Point: sequence must have 2 items, got {len(x)}")
            raw_x, raw_y = x[0], x[1]
        else:
            if y is None:
                raise TypeError("Point: 'y' is required when 'x' is a number")
            raw_x, raw_y = x, y

        self.x = self._to_int(raw_x, "x")
        self.y = self._to_int(raw_y, "y")

    @staticmethod
    def _to_int(value: Number, name: str) -> int:
        """ Приводит координату к int: дробные (в т.ч. numpy.float32) округляются, остальное — через int(). """
        if isinstance(value, Real) and not isinstance(value, Integral):
            return round(float(value))
        try:
            return int(value)
        except (TypeError, ValueError) as e:
            raise TypeError(f"Point: can't convert {name}={value!r} to int") from e

    def __add__(self, point: Point) -> Point:
        """ (x1 + x2, y1 + y2) """
        return Point(self.x + point.x, self.y + point.y)

    def __sub__(self, point: Point) -> Point:
        """ (x1 - x2, y1 - y2) """
        return Point(self.x - point.x, self.y - point.y)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"

    def distance_to(self, point: Point) -> int:
        """ Евклидово расстояние до точки, округлённое до int. """
        return round(sqrt((self.x - point.x) ** 2 + (self.y - point.y) ** 2))

    def tuple(self) -> builtins.tuple[int, int]:
        """ (x, y) """
        return self.x, self.y

    def list(self) -> builtins.list[int]:
        """ [x, y] """
        return [self.x, self.y]
