""" Прямоугольник: по осям (bounding rect) или повёрнутый (минимальной площади, через OpenCV). """

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np
import numpy.typing as npt

from ._box_utils import bounding_rect_xywh, box_to_coords
from ._cv import min_area_rect
from ._polygon import shoelace_area
from .contour import Contour
from .point import Point
from .types import Angle, Area, CvContour, Height, IntCoords, Width


class Rectangle:
    """
    Прямоугольник, описанный вокруг контура.

    rotated=False — прямоугольник по осям, как cv2.boundingRect (границы включительные: w = xmax - xmin + 1).
    rotated=True — прямоугольник минимальной площади, как cv2.minAreaRect + cv2.boxPoints;
    требует OpenCV (`pip install neuro-geometry[cv]`). Углы lbp/ltp/rtp/rbp берутся из cv2.boxPoints
    в его порядке, поэтому для повёрнутого прямоугольника их имена условны.
    """

    _contour: CvContour  # контур (4, 1, 2) int32
    _coords: IntCoords  # [lbp, ltp, rtp, rbp]

    _lbp: Point  # левая нижняя точка
    _ltp: Point  # левая верхняя точка
    _rtp: Point  # правая верхняя точка
    _rbp: Point  # правая нижняя точка

    _cp: Point  # центральная точка
    _lcp: Point  # середина левой стороны
    _rcp: Point  # середина правой стороны
    _tcp: Point  # середина верхней стороны
    _bcp: Point  # середина нижней стороны

    _area: Area
    _width: Width
    _height: Height
    _angle: Angle  # угол наклона относительно оси X (cv2.minAreaRect), 0 для rotated=False
    _rotated: bool

    def __init__(self, contour_or_box: CvContour | Sequence[float] | Sequence[Sequence[float]], rotated: bool = False):
        """
        contour_or_box — контур OpenCV (N, 1, 2) / массив (N, 2), либо список вида
        [x1, y1, x2, y2, ...] или [[x1, y1], [x2, y2], ...].
        """
        if isinstance(contour_or_box, np.ndarray):
            points: npt.NDArray[np.generic] = contour_or_box.reshape(-1, 2)
        else:
            points = Contour.get_from_coords(box_to_coords(contour_or_box)).reshape(-1, 2)
        if points.shape[0] < 2:
            raise ValueError(f"Rectangle requires at least 2 points, got {points.shape[0]}")

        if rotated:
            ((cx, cy), (size_w, size_h), angle), box = min_area_rect(points)
            if angle > 45 or angle < -45:
                width, height = round(size_h), round(size_w)
            else:
                width, height = round(size_w), round(size_h)
            lbp, ltp, rtp, rbp = (Point(float(x), float(y)) for x, y in box)
            self._assign(lbp, ltp, rtp, rbp, Point(cx, cy), width, height, angle, rotated=True)
        else:
            x, y, width, height = bounding_rect_xywh(points)
            ltp = Point(x, y)
            self._assign(
                lbp=Point(x, y + height),
                ltp=ltp,
                rtp=Point(x + width, y),
                rbp=Point(x + width, y + height),
                cp=Point(x + round(width / 2), y + round(height / 2)),
                width=width,
                height=height,
                angle=0.0,
                rotated=False,
            )

    def _assign(
        self,
        lbp: Point,
        ltp: Point,
        rtp: Point,
        rbp: Point,
        cp: Point,
        width: Width,
        height: Height,
        angle: Angle,
        rotated: bool,
    ) -> None:
        """ Устанавливает углы и пересчитывает все производные величины. """
        self._lbp, self._ltp, self._rtp, self._rbp = lbp, ltp, rtp, rbp
        self._cp = cp
        self._width = width
        self._height = height
        self._angle = angle
        self._rotated = rotated

        self._coords = [lbp.list(), ltp.list(), rtp.list(), rbp.list()]
        self._contour = Contour.get_from_coords(self._coords)
        # Середины сторон считаются от ltp по осям — для повёрнутого прямоугольника это приближение
        half_height = round(height / 2)
        self._lcp = Point(ltp.x, ltp.y + half_height)
        self._rcp = Point(ltp.x + width, ltp.y + half_height)
        self._tcp = Point(cp.x, ltp.y)
        self._bcp = Point(cp.x, lbp.y)
        self._area = shoelace_area([lbp, ltp, rtp, rbp])

    def _copy_with(
        self, lbp: Point, ltp: Point, rtp: Point, rbp: Point, cp: Point, width: Width, height: Height
    ) -> Rectangle:
        """ Новый прямоугольник с теми же углом и типом, без повторного вписывания в контур. """
        rect = Rectangle.__new__(Rectangle)
        rect._assign(lbp, ltp, rtp, rbp, cp, width, height, self._angle, self._rotated)
        return rect

    @property
    def area(self) -> Area:
        """ Площадь по вершинам. """
        return self._area

    @property
    def contour(self) -> CvContour:
        """ Контур (4, 1, 2) int32 из вершин [lbp, ltp, rtp, rbp]. """
        return self._contour

    @property
    def angle(self) -> Angle:
        """ Угол из cv2.minAreaRect; 0 для прямоугольника по осям. """
        return self._angle

    @property
    def rotated(self) -> bool:
        """ True, если прямоугольник построен как повёрнутый (minAreaRect). """
        return self._rotated

    @property
    def ltp(self) -> Point:
        """ Левая верхняя точка. """
        return self._ltp

    @property
    def lbp(self) -> Point:
        """ Левая нижняя точка. """
        return self._lbp

    @property
    def rtp(self) -> Point:
        """ Правая верхняя точка. """
        return self._rtp

    @property
    def rbp(self) -> Point:
        """ Правая нижняя точка. """
        return self._rbp

    @property
    def cp(self) -> Point:
        """ Центральная точка. """
        return self._cp

    @property
    def lcp(self) -> Point:
        """ Середина левой стороны. """
        return self._lcp

    @property
    def rcp(self) -> Point:
        """ Середина правой стороны. """
        return self._rcp

    @property
    def tcp(self) -> Point:
        """ Середина верхней стороны. """
        return self._tcp

    @property
    def bcp(self) -> Point:
        """ Середина нижней стороны. """
        return self._bcp

    @property
    def width(self) -> Width:
        return self._width

    @property
    def height(self) -> Height:
        return self._height

    @property
    def coords(self) -> IntCoords:
        """ [lbp, ltp, rtp, rbp] """
        return self._coords

    def shift(self, shift_point: Point) -> None:
        """ Сдвигает прямоугольник на вектор shift_point; все производные точки пересчитываются. """
        self._assign(
            self._lbp + shift_point,
            self._ltp + shift_point,
            self._rtp + shift_point,
            self._rbp + shift_point,
            self._cp + shift_point,
            self._width,
            self._height,
            self._angle,
            self._rotated,
        )

    def shift_given_angle(self, shift: int) -> Rectangle:
        """
        Параллельный прямоугольник, сдвинутый на shift пикселей вдоль оси наклона:
        при angle < 45 — вдоль ширины, иначе — перпендикулярно (вдоль высоты).
        """
        angle_rad = math.radians(self._angle)
        if self._angle < 45:
            vector = Point(shift * math.cos(angle_rad), shift * math.sin(angle_rad))
        else:
            vector = Point(shift * math.sin(angle_rad), -shift * math.cos(angle_rad))
        return self._copy_with(
            self._lbp + vector,
            self._ltp + vector,
            self._rtp + vector,
            self._rbp + vector,
            self._cp + vector,
            self._width,
            self._height,
        )

    def decrease(self, width_percent: float, height_percent: float) -> Rectangle:
        """
        Уменьшенный прямоугольник с тем же центром и углом: каждая сторона сдвигается внутрь
        на width_percent % ширины и height_percent % высоты. Текущий прямоугольник не меняется.
        """
        width_k = 1 - 2 * width_percent / 100
        height_k = 1 - 2 * height_percent / 100
        if width_k < 0 or height_k < 0:
            raise ValueError("Decrease percent must not exceed 50")

        corners = np.array(self._coords, dtype=np.float64)
        center = corners.mean(axis=0)
        # Оси прямоугольника: lbp→rbp (ширина) и lbp→ltp (высота)
        axis_w = corners[3] - corners[0]
        axis_h = corners[1] - corners[0]
        axis_w /= np.linalg.norm(axis_w) or 1.0
        axis_h /= np.linalg.norm(axis_h) or 1.0
        offsets = corners - center
        scaled = (
            center
            + np.outer(offsets @ axis_w * width_k, axis_w)
            + np.outer(offsets @ axis_h * height_k, axis_h)
        )
        lbp, ltp, rtp, rbp = (Point(float(x), float(y)) for x, y in scaled)
        return self._copy_with(
            lbp, ltp, rtp, rbp, self._cp, round(self._width * width_k), round(self._height * height_k)
        )
