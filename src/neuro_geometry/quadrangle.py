""" Произвольный четырёхугольник. """

from __future__ import annotations

import math

import numpy as np
import numpy.typing as npt

from ._rounding import readonly, to_contour
from .point import Point
from .types import Coords, CvContour, FloatArray

# Индексы вершин во внутреннем массиве
_LB, _LT, _RT, _RB = 0, 1, 2, 3


def _parse_vertices(vertices: npt.ArrayLike) -> list[list[float]]:
    """ Вершины -> список [x, y] float; для списков без numpy (на 4 точках он медленнее). """
    if isinstance(vertices, (list, tuple)) and all(isinstance(v, (list, tuple)) and len(v) == 2 for v in vertices):
        return [[float(v[0]), float(v[1])] for v in vertices]
    pts: list[list[float]] = np.asarray(vertices, dtype=np.float64).reshape(-1, 2).tolist()
    return pts


def _order_corners(pts: list[list[float]]) -> list[list[float]]:
    """
    Упорядочивает 4 вершины в [lbp, ltp, rtp, rbp].
    Вершины сортируются по углу вокруг центроида (по часовой на изображении),
    первой (ltp) становится вершина с минимальным x + y, при равенстве — с меньшим y.
    """
    cx = sum(p[0] for p in pts) / 4
    cy = sum(p[1] for p in pts) / 4
    by_angle = sorted(pts, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
    start = min(range(4), key=lambda i: (by_angle[i][0] + by_angle[i][1], by_angle[i][1]))
    ltp, rtp, rbp, lbp = by_angle[start:] + by_angle[:start]
    return [lbp, ltp, rtp, rbp]


class Quadrangle:
    """
    Четырёхугольник с вершинами lbp, ltp, rtp, rbp (левая нижняя, левая верхняя, правая верхняя, правая нижняя).
    Вершины в любом порядке упорядочиваются автоматически. Ось Y направлена вниз.

    Изменение на месте (возвращают None): shift(), scale(), decrease(), increase().
    Новый объект: shifted(), scaled(), decreased(), increased(), copy().
    """

    __slots__ = ("_contour", "_pts")

    def __init__(self, vertices: npt.ArrayLike) -> None:
        pts = _parse_vertices(vertices)
        if len(pts) != 4:
            raise ValueError(f"Quadrangle requires exactly 4 vertices, got {len(pts)}")
        self._pts: list[list[float]] = _order_corners(pts)
        self._contour: CvContour | None = None

    @classmethod
    def from_box(cls, x1: float, y1: float, x2: float, y2: float) -> Quadrangle:
        """ Прямоугольник по осям из двух противоположных углов. """
        return cls([[x1, y1], [x1, y2], [x2, y2], [x2, y1]])

    @classmethod
    def from_points(cls, points: npt.ArrayLike) -> Quadrangle:
        """
        Четырёхугольник по крайним точкам набора (>= 4 точек): ltp — min(x + y), rbp — max(x + y),
        rtp — max(x - y), lbp — min(x - y). Подходит для фигур, повёрнутых менее чем на 45°.
        """
        pts = np.asarray(points, dtype=np.float64).reshape(-1, 2)
        if pts.shape[0] < 4:
            raise ValueError(f"Quadrangle.from_points requires at least 4 points, got {pts.shape[0]}")
        s, d = pts[:, 0] + pts[:, 1], pts[:, 0] - pts[:, 1]
        return cls(pts[[np.argmin(d), np.argmin(s), np.argmax(d), np.argmax(s)]])

    def copy(self) -> Quadrangle:
        """ Независимая копия. """
        quad = Quadrangle.__new__(Quadrangle)
        quad._pts = [p.copy() for p in self._pts]
        quad._contour = None
        return quad

    # --- производные величины ---

    def _point(self, i: int) -> Point:
        return Point(self._pts[i][0], self._pts[i][1])

    def _middle(self, i: int, j: int) -> Point:
        (xi, yi), (xj, yj) = self._pts[i], self._pts[j]
        return Point((xi + xj) / 2, (yi + yj) / 2)

    def _dist(self, i: int, j: int) -> float:
        (xi, yi), (xj, yj) = self._pts[i], self._pts[j]
        return math.hypot(xi - xj, yi - yj)

    def _mean(self) -> tuple[float, float]:
        return sum(p[0] for p in self._pts) / 4, sum(p[1] for p in self._pts) / 4

    @property
    def lbp(self) -> Point:
        return self._point(_LB)

    @property
    def ltp(self) -> Point:
        return self._point(_LT)

    @property
    def rtp(self) -> Point:
        return self._point(_RT)

    @property
    def rbp(self) -> Point:
        return self._point(_RB)

    @property
    def cp(self) -> Point:
        """ Среднее вершин. """
        x, y = self._mean()
        return Point(x, y)

    @property
    def lcp(self) -> Point:
        """ Середина левой стороны. """
        return self._middle(_LB, _LT)

    @property
    def tcp(self) -> Point:
        """ Середина верхней стороны. """
        return self._middle(_LT, _RT)

    @property
    def rcp(self) -> Point:
        """ Середина правой стороны. """
        return self._middle(_RT, _RB)

    @property
    def bcp(self) -> Point:
        """ Середина нижней стороны. """
        return self._middle(_RB, _LB)

    @property
    def left_height(self) -> float:
        return self._dist(_LB, _LT)

    @property
    def top_width(self) -> float:
        return self._dist(_LT, _RT)

    @property
    def right_height(self) -> float:
        return self._dist(_RT, _RB)

    @property
    def bottom_width(self) -> float:
        return self._dist(_RB, _LB)

    @property
    def min_width(self) -> float:
        return min(self.top_width, self.bottom_width)

    @property
    def max_width(self) -> float:
        return max(self.top_width, self.bottom_width)

    @property
    def min_height(self) -> float:
        return min(self.left_height, self.right_height)

    @property
    def max_height(self) -> float:
        return max(self.left_height, self.right_height)

    @property
    def area(self) -> float:
        """ Площадь по формуле шнурования. """
        pts = self._pts
        twice = sum(pts[i][0] * pts[i - 3][1] - pts[i - 3][0] * pts[i][1] for i in range(4))
        return abs(twice) / 2

    @property
    def corners(self) -> FloatArray:
        """ Вершины [lbp, ltp, rtp, rbp] новым массивом (4, 2) float64. """
        return np.array(self._pts, dtype=np.float64)

    @property
    def coords(self) -> Coords:
        """ Вершины [lbp, ltp, rtp, rbp] списком. """
        return [p.copy() for p in self._pts]

    @property
    def contour(self) -> CvContour:
        """ Контур OpenCV (4, 1, 2) int32, только для чтения (кэшируется). """
        if self._contour is None:
            self._contour = to_contour(self._pts)
        return readonly(self._contour)

    # --- изменение на месте ---

    def shift(self, dx: float, dy: float) -> None:
        """ Сдвигает на месте. """
        for p in self._pts:
            p[0] += dx
            p[1] += dy
        self._contour = None

    def scale(self, x_k: float, y_k: float | None = None) -> None:
        """ Масштабирует относительно среднего вершин по осям X и Y на месте. """
        y_k = x_k if y_k is None else y_k
        if x_k < 0 or y_k < 0:
            raise ValueError("Scale factors must be non-negative")
        cx, cy = self._mean()
        for p in self._pts:
            p[0] = cx + (p[0] - cx) * x_k
            p[1] = cy + (p[1] - cy) * y_k
        self._contour = None

    def decrease(self, width_percent: float, height_percent: float | None = None) -> None:
        """ Уменьшает на месте: по каждой стороне на заданный процент размера по X/Y. """
        height_percent = width_percent if height_percent is None else height_percent
        if width_percent > 50 or height_percent > 50:
            raise ValueError("Decrease percent must not exceed 50")
        self.scale(1 - 2 * width_percent / 100, 1 - 2 * height_percent / 100)

    def increase(self, width_percent: float, height_percent: float | None = None) -> None:
        """ Увеличивает на месте: по каждой стороне на заданный процент размера по X/Y. """
        height_percent = width_percent if height_percent is None else height_percent
        self.scale(1 + 2 * width_percent / 100, 1 + 2 * height_percent / 100)

    # --- новый объект ---

    def shifted(self, dx: float, dy: float) -> Quadrangle:
        quad = self.copy()
        quad.shift(dx, dy)
        return quad

    def scaled(self, x_k: float, y_k: float | None = None) -> Quadrangle:
        quad = self.copy()
        quad.scale(x_k, y_k)
        return quad

    def decreased(self, width_percent: float, height_percent: float | None = None) -> Quadrangle:
        quad = self.copy()
        quad.decrease(width_percent, height_percent)
        return quad

    def increased(self, width_percent: float, height_percent: float | None = None) -> Quadrangle:
        quad = self.copy()
        quad.increase(width_percent, height_percent)
        return quad

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Quadrangle):
            return NotImplemented
        return self._pts == other._pts

    __hash__ = None  # type: ignore[assignment]

    def __repr__(self) -> str:
        return f"Quadrangle({self.coords})"
