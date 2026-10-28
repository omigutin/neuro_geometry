""" Треугольник. """

from __future__ import annotations

import math

import numpy as np
import numpy.typing as npt

from ._rounding import to_contour
from .point import Point
from .types import Coords, CvContour, FloatArray


class Triangle:
    """
    Треугольник с вершинами a, b, c в переданном порядке.

    Изменение на месте (возвращает None): shift().
    Новый объект: shifted(), copy().
    """

    __slots__ = ("_pts",)

    def __init__(self, a: Point, b: Point, c: Point) -> None:
        self._pts: list[list[float]] = [[a.x, a.y], [b.x, b.y], [c.x, c.y]]

    @classmethod
    def from_coords(cls, coords: npt.ArrayLike) -> Triangle:
        """ Треугольник из [[x, y], [x, y], [x, y]]. """
        pts = np.asarray(coords, dtype=np.float64).reshape(-1, 2)
        if pts.shape[0] != 3:
            raise ValueError(f"Triangle requires exactly 3 vertices, got {pts.shape[0]}")
        return cls(*(Point(x, y) for x, y in pts))

    def copy(self) -> Triangle:
        tri = Triangle.__new__(Triangle)
        tri._pts = [p.copy() for p in self._pts]
        return tri

    def _point(self, i: int) -> Point:
        return Point(self._pts[i][0], self._pts[i][1])

    def _dist(self, i: int, j: int) -> float:
        (xi, yi), (xj, yj) = self._pts[i], self._pts[j]
        return math.hypot(xi - xj, yi - yj)

    @property
    def a(self) -> Point:
        return self._point(0)

    @property
    def b(self) -> Point:
        return self._point(1)

    @property
    def c(self) -> Point:
        return self._point(2)

    @property
    def ab(self) -> float:
        """ Длина стороны a–b. """
        return self._dist(0, 1)

    @property
    def bc(self) -> float:
        """ Длина стороны b–c. """
        return self._dist(1, 2)

    @property
    def ca(self) -> float:
        """ Длина стороны c–a. """
        return self._dist(2, 0)

    @property
    def perimeter(self) -> float:
        return self.ab + self.bc + self.ca

    @property
    def area(self) -> float:
        (ax, ay), (bx, by), (cx, cy) = self._pts
        return abs((bx - ax) * (cy - ay) - (cx - ax) * (by - ay)) / 2

    @property
    def centroid(self) -> Point:
        return Point(sum(p[0] for p in self._pts) / 3, sum(p[1] for p in self._pts) / 3)

    @property
    def corners(self) -> FloatArray:
        """ Вершины [a, b, c] новым массивом (3, 2) float64. """
        return np.array(self._pts, dtype=np.float64)

    @property
    def coords(self) -> Coords:
        return [p.copy() for p in self._pts]

    @property
    def contour(self) -> CvContour:
        return to_contour(self._pts)

    def shift(self, dx: float, dy: float) -> None:
        """ Сдвигает на месте. """
        for p in self._pts:
            p[0] += dx
            p[1] += dy

    def shifted(self, dx: float, dy: float) -> Triangle:
        tri = self.copy()
        tri.shift(dx, dy)
        return tri

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Triangle):
            return NotImplemented
        return self._pts == other._pts

    __hash__ = None  # type: ignore[assignment]

    def __repr__(self) -> str:
        return f"Triangle({self.coords})"
