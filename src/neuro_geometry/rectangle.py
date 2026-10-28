""" Прямоугольник, в том числе повёрнутый. """

from __future__ import annotations

import math

import numpy as np
import numpy.typing as npt

from ._cv import min_area_rect
from ._rounding import readonly, round_half_up, to_contour
from .point import Point
from .types import Coords, CvContour, FloatArray


class Rectangle:
    """
    Прямоугольник: центр (cx, cy), размеры (width, height) и угол поворота angle в градусах.

    Угол нормализуется в (-45, 45]: width — сторона, более близкая к горизонтали, height — к вертикали.
    Углы lbp, ltp, rtp, rbp и середины сторон заданы в системе самого прямоугольника,
    поэтому их имена корректны и для повёрнутого прямоугольника. Ось Y направлена вниз.

    Изменение на месте (возвращают None): shift(), shift_along_axes(), scale(), decrease(), increase(),
    set_center(), сеттеры width, height, angle.
    Новый объект: shifted(), shifted_along_axes(), scaled(), decreased(), increased(), copy().
    Вершины и контур считаются лениво и кэшируются; shift() сдвигает кэш на месте.
    """

    __slots__ = ("_angle", "_contour", "_corners", "_cx", "_cy", "_h", "_w")

    def __init__(self, cx: float, cy: float, width: float, height: float, angle: float = 0.0) -> None:
        if width < 0 or height < 0:
            raise ValueError(f"Rectangle size must be non-negative, got {width}x{height}")
        self._cx, self._cy = float(cx), float(cy)
        self._w, self._h = float(width), float(height)
        self._angle = float(angle)
        self._corners: FloatArray | None = None
        self._contour: CvContour | None = None
        if self._angle != 0.0:
            self._normalize_angle()

    # --- конструкторы ---

    @classmethod
    def from_xywh(cls, x: float, y: float, width: float, height: float) -> Rectangle:
        """ По левому верхнему углу и размерам, например из cv2.boundingRect. """
        return cls(x + width / 2, y + height / 2, width, height)

    @classmethod
    def from_box(cls, x1: float, y1: float, x2: float, y2: float) -> Rectangle:
        """ По двум противоположным углам (порядок не важен). """
        left, right = min(x1, x2), max(x1, x2)
        top, bottom = min(y1, y2), max(y1, y2)
        return cls((left + right) / 2, (top + bottom) / 2, right - left, bottom - top)

    @classmethod
    def from_points(cls, points: npt.ArrayLike, rotated: bool = False) -> Rectangle:
        """
        Описанный прямоугольник вокруг точек: (N, 2), (N, 1, 2) или список пар.
        rotated=False — по осям, width = xmax - xmin (геометрическая ширина, без +1 как у cv2.boundingRect).
        rotated=True — минимальной площади через cv2.minAreaRect (нужен OpenCV).
        """
        pts = np.asarray(points, dtype=np.float64).reshape(-1, 2)
        if pts.shape[0] == 0:
            raise ValueError("Rectangle requires at least 1 point")
        if not rotated:
            (xmin, ymin), (xmax, ymax) = pts.min(axis=0), pts.max(axis=0)
            return cls.from_box(float(xmin), float(ymin), float(xmax), float(ymax))

        (cx, cy), (w, h), angle = min_area_rect(pts)
        return cls(cx, cy, w, h, angle)

    def _normalize_angle(self) -> None:
        """ Приводит угол в (-45, 45], меняя местами стороны при повороте на 90°. """
        angle = math.remainder(self._angle, 180.0)  # [-90, 90]
        if angle > 45:
            angle -= 90
            self._w, self._h = self._h, self._w
        elif angle <= -45:
            angle += 90
            self._w, self._h = self._h, self._w
        self._angle = angle
        self._invalidate()

    def copy(self) -> Rectangle:
        """ Независимая копия (кэш не копируется). """
        return Rectangle(self._cx, self._cy, self._w, self._h, self._angle)

    # --- состояние ---

    def _invalidate(self) -> None:
        self._corners = None
        self._contour = None

    @property
    def cx(self) -> float:
        return self._cx

    @property
    def cy(self) -> float:
        return self._cy

    @property
    def width(self) -> float:
        return self._w

    @width.setter
    def width(self, value: float) -> None:
        if value < 0:
            raise ValueError(f"width must be non-negative, got {value}")
        self._w = float(value)
        self._invalidate()

    @property
    def height(self) -> float:
        return self._h

    @height.setter
    def height(self, value: float) -> None:
        if value < 0:
            raise ValueError(f"height must be non-negative, got {value}")
        self._h = float(value)
        self._invalidate()

    @property
    def angle(self) -> float:
        """ Угол поворота в градусах; положительный — по часовой стрелке на изображении. """
        return self._angle

    @angle.setter
    def angle(self, value: float) -> None:
        self._angle = float(value)
        self._normalize_angle()

    @property
    def is_axis_aligned(self) -> bool:
        return self._angle == 0.0

    def set_center(self, cx: float, cy: float) -> None:
        """ Переносит центр на месте. """
        self.shift(cx - self._cx, cy - self._cy)

    # --- производные величины ---

    def _local(self, u: float, v: float) -> tuple[float, float]:
        """ Точка (u, v) из системы прямоугольника (центр в 0) в координаты изображения. """
        if self._angle == 0.0:
            return self._cx + u, self._cy + v
        rad = math.radians(self._angle)
        cos, sin = math.cos(rad), math.sin(rad)
        return self._cx + u * cos - v * sin, self._cy + u * sin + v * cos

    def _local_point(self, u: float, v: float) -> Point:
        x, y = self._local(u, v)
        return Point(x, y)

    @property
    def cp(self) -> Point:
        """ Центр. """
        return Point(self._cx, self._cy)

    @property
    def lbp(self) -> Point:
        """ Левая нижняя вершина. """
        return self._local_point(-self._w / 2, self._h / 2)

    @property
    def ltp(self) -> Point:
        """ Левая верхняя вершина. """
        return self._local_point(-self._w / 2, -self._h / 2)

    @property
    def rtp(self) -> Point:
        """ Правая верхняя вершина. """
        return self._local_point(self._w / 2, -self._h / 2)

    @property
    def rbp(self) -> Point:
        """ Правая нижняя вершина. """
        return self._local_point(self._w / 2, self._h / 2)

    @property
    def lcp(self) -> Point:
        """ Середина левой стороны. """
        return self._local_point(-self._w / 2, 0.0)

    @property
    def rcp(self) -> Point:
        """ Середина правой стороны. """
        return self._local_point(self._w / 2, 0.0)

    @property
    def tcp(self) -> Point:
        """ Середина верхней стороны. """
        return self._local_point(0.0, -self._h / 2)

    @property
    def bcp(self) -> Point:
        """ Середина нижней стороны. """
        return self._local_point(0.0, self._h / 2)

    @property
    def area(self) -> float:
        return self._w * self._h

    def _corners_array(self) -> FloatArray:
        if self._corners is None:
            hw, hh = self._w / 2, self._h / 2
            self._corners = np.array(
                [self._local(-hw, hh), self._local(-hw, -hh), self._local(hw, -hh), self._local(hw, hh)],
                dtype=np.float64,
            )
        return self._corners

    @property
    def corners(self) -> FloatArray:
        """ Вершины [lbp, ltp, rtp, rbp] массивом (4, 2) float64, только для чтения. """
        return readonly(self._corners_array())

    @property
    def coords(self) -> Coords:
        """ Вершины [lbp, ltp, rtp, rbp] списком. """
        coords: Coords = self._corners_array().tolist()
        return coords

    @property
    def contour(self) -> CvContour:
        """ Контур OpenCV (4, 1, 2) int32 из вершин [lbp, ltp, rtp, rbp], только для чтения. """
        if self._contour is None:
            self._contour = to_contour(self._corners_array())
        return readonly(self._contour)

    def bounding_box(self) -> tuple[float, float, float, float]:
        """ Описанный прямоугольник по осям: (x1, y1, x2, y2). """
        if self._angle == 0.0:
            hw, hh = self._w / 2, self._h / 2
            return self._cx - hw, self._cy - hh, self._cx + hw, self._cy + hh
        corners = self._corners_array()
        (x1, y1), (x2, y2) = corners.min(axis=0), corners.max(axis=0)
        return float(x1), float(y1), float(x2), float(y2)

    def to_int_box(self) -> tuple[int, int, int, int]:
        """ bounding_box() в пикселях (округление половины вверх) — например, для вырезки image[y1:y2, x1:x2]. """
        x1, y1, x2, y2 = self.bounding_box()
        return round_half_up(x1), round_half_up(y1), round_half_up(x2), round_half_up(y2)

    def contains(self, point: Point, eps: float = 1e-9) -> bool:
        """ Лежит ли точка внутри прямоугольника или на границе. """
        dx, dy = point.x - self._cx, point.y - self._cy
        if self._angle != 0.0:
            rad = math.radians(self._angle)
            cos, sin = math.cos(rad), math.sin(rad)
            dx, dy = dx * cos + dy * sin, -dx * sin + dy * cos
        return abs(dx) <= self._w / 2 + eps and abs(dy) <= self._h / 2 + eps

    # --- изменение на месте ---

    def shift(self, dx: float, dy: float) -> None:
        """ Сдвигает прямоугольник на месте. """
        self._cx += dx
        self._cy += dy
        if self._corners is not None:
            self._corners[:, 0] += dx
            self._corners[:, 1] += dy
        self._contour = None

    def shift_along_axes(self, along_width: float, along_height: float = 0.0) -> None:
        """ Сдвигает на месте вдоль собственных осей прямоугольника (вдоль ширины и вдоль высоты). """
        dx, dy = self._local(along_width, along_height)
        self.shift(dx - self._cx, dy - self._cy)

    def scale(self, width_k: float, height_k: float | None = None) -> None:
        """ Масштабирует размеры относительно центра на месте. """
        height_k = width_k if height_k is None else height_k
        if width_k < 0 or height_k < 0:
            raise ValueError("Scale factors must be non-negative")
        self._w *= width_k
        self._h *= height_k
        self._invalidate()

    def decrease(self, width_percent: float, height_percent: float | None = None) -> None:
        """ Уменьшает на месте: каждая сторона сдвигается внутрь на заданный процент ширины/высоты. """
        height_percent = width_percent if height_percent is None else height_percent
        if width_percent > 50 or height_percent > 50:
            raise ValueError("Decrease percent must not exceed 50")
        self.scale(1 - 2 * width_percent / 100, 1 - 2 * height_percent / 100)

    def increase(self, width_percent: float, height_percent: float | None = None) -> None:
        """ Увеличивает на месте: каждая сторона сдвигается наружу на заданный процент ширины/высоты. """
        height_percent = width_percent if height_percent is None else height_percent
        self.scale(1 + 2 * width_percent / 100, 1 + 2 * height_percent / 100)

    # --- новый объект ---

    def shifted(self, dx: float, dy: float) -> Rectangle:
        """ Новый прямоугольник, сдвинутый на (dx, dy). """
        return Rectangle(self._cx + dx, self._cy + dy, self._w, self._h, self._angle)

    def shifted_along_axes(self, along_width: float, along_height: float = 0.0) -> Rectangle:
        """ Новый прямоугольник, сдвинутый вдоль собственных осей. """
        cx, cy = self._local(along_width, along_height)
        return Rectangle(cx, cy, self._w, self._h, self._angle)

    def scaled(self, width_k: float, height_k: float | None = None) -> Rectangle:
        rect = self.copy()
        rect.scale(width_k, height_k)
        return rect

    def decreased(self, width_percent: float, height_percent: float | None = None) -> Rectangle:
        rect = self.copy()
        rect.decrease(width_percent, height_percent)
        return rect

    def increased(self, width_percent: float, height_percent: float | None = None) -> Rectangle:
        rect = self.copy()
        rect.increase(width_percent, height_percent)
        return rect

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Rectangle):
            return NotImplemented
        return (self._cx, self._cy, self._w, self._h, self._angle) == (
            other._cx, other._cy, other._w, other._h, other._angle
        )

    __hash__ = None  # type: ignore[assignment]

    def __repr__(self) -> str:
        return (
            f"Rectangle(cx={self._cx:g}, cy={self._cy:g}, width={self._w:g}, height={self._h:g}, "
            f"angle={self._angle:g})"
        )
