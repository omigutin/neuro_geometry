from __future__ import annotations

from typing import Union

import numpy as np

from ._box_utils import box_to_coords
from .contour import Contour
from ._rotcalipers import bounding_rect_xywh, min_area_rect, rotated_rect_box_points
from .point import Point
from .types import Angle, Area, Coords, CvContour, Height, Width


class Rectangle(object):
    _contour: CvContour  # контур
    _coords: Coords  # упорядоченные координаты

    _lbp: Point  # левая нижняя точка
    _ltp: Point  # левая верхняя точка
    _rtp: Point  # правая верхняя точка
    _rbp: Point  # правая нижняя точка

    _cp: Point  # центральная точка
    _lcp: Point  # левая средняя точка
    _rcp: Point  # правая средняя точка
    _tcp: Point  # Центральная точка на верхней стороне
    _bcp: Point  # Центральная точка на нижней стороне

    _area: Area
    _width: Width
    _height: Height
    _angle: Angle  # угол наклона относительно оси X

    # инициализация от левой верхней точки, ширины и высоты
    def __init__(self, contour_or_box: Union[CvContour, list[int]], rotated: bool = False):
        if isinstance(contour_or_box, list):
            coords = box_to_coords(contour_or_box)
            contour = Contour.get_from_coords(coords)
        else:
            contour = contour_or_box

        if contour.shape[0] < 2 and contour.shape[1] < 2:
            raise Exception(f"Contour shape must be more (2, 2).")

        # Если надо учитывать угол вращения, находим минимальный прямоугольник, описывающий контур,
        # учитывая угол вращения
        if rotated:
            rr = min_area_rect(contour.reshape(-1, 2).astype(np.float32))
            rect_box = rotated_rect_box_points(rr.center, rr.size, rr.angle_deg)
            self._angle = rr.angle_deg

            if self._angle > 45 or self._angle < -45:
                self._height = round(rr.size[0])
                self._width = round(rr.size[1])
            else:
                self._height = round(rr.size[1])
                self._width = round(rr.size[0])

            self._cp = Point(rr.center[0], rr.center[1])
            rb = rect_box.tolist()
            self._lbp = Point(rb[0][0], rb[0][1])
            self._ltp = Point(rb[1][0], rb[1][1])
            self._rtp = Point(rb[2][0], rb[2][1])
            self._rbp = Point(rb[3][0], rb[3][1])
        else:
            self._angle = 0
            # rect = x левой верхней точки, y левой верхней точки, ширина, высота
            # TODO: На 1 пиксель даёт больший прямоугольник. Мешает вырезке crop зоны нужного размера
            rect = bounding_rect_xywh(contour)
            self._width = round(rect[2])
            self._height = round(rect[3])
            self._ltp = Point(round(rect[0]), round(rect[1]))
            self._lbp = Point(self._ltp.x, self._ltp.y + self._height)
            self._rtp = Point(self._ltp.x + self._width, self._ltp.y)
            self._rbp = Point(self._ltp.x + self._width, self._ltp.y + self._height)
            self._cp = Point(self._ltp.x + round(self._width / 2), self._ltp.y + round(self._height / 2))

        self._coords = Coords([self._lbp.list(), self._ltp.list(), self._rtp.list(), self._rbp.list()])
        self._contour = np.array(self._coords, dtype=np.int32)
        self._contour = self._contour.reshape((-1, 1, 2))

        self._lcp = Point(self._ltp.x, self._ltp.y + round(self._height / 2))
        self._rcp = Point(self._ltp.x + self._width, self._ltp.y + round(self._height / 2))
        self._tcp = Point(self._cp.x, self._ltp.y)
        self._bcp = Point(self._cp.x, self._lbp.y)

        self._bottom_width = self._lbp.distance_to(self._rbp)
        self._top_width = self._ltp.distance_to(self._rtp)
        self._left_height = self._lbp.distance_to(self._ltp)
        self._right_height = self._rbp.distance_to(self._rtp)

        self._area = self._get_area()

    # Вычисляет площадь
    def _get_area(self) -> Area:
        half_perimeter = 0.5 * (self._left_height + self._top_width + self._right_height + self._bottom_width)
        area = (half_perimeter - self._left_height) * (half_perimeter - self._top_width) * (
            half_perimeter - self._right_height
        ) * (half_perimeter - self._bottom_width)
        area = pow(area, 0.5)
        return area

    @property
    def area(self) -> Area:
        return self._area

    @property
    def contour(self) -> CvContour:
        return self._contour

    @property
    def angle(self) -> Angle:
        return self._angle

    # левая верхняя точка
    @property
    def ltp(self):
        return self._ltp

    # левая нижняя точка
    @property
    def lbp(self):
        return self._lbp

    # правая верхняя точка
    @property
    def rtp(self):
        return self._rtp

    # правая нижняя точка
    @property
    def rbp(self):
        return self._rbp

    # центральная точка
    @property
    def cp(self):
        return self._cp

    # левая средняя точка
    @property
    def lcp(self):
        return self._lcp

    # правая средняя точка
    @property
    def rcp(self):
        return self._rcp

    @property
    def tcp(self):
        """Центральная точка на верхней стороне"""
        return self._tcp

    @property
    def bcp(self):
        """Центральная точка на нижней стороне"""
        return self._bcp

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def coords(self):
        return self._coords

    # Сдвигает углы на заданную точку
    def shift(self, shift_point: Point) -> None:
        self._lbp = Point(self._lbp.x + shift_point.x, self._lbp.y + shift_point.y)
        self._ltp = Point(self._ltp.x + shift_point.x, self._ltp.y + shift_point.y)
        self._rbp = Point(self._rbp.x + shift_point.x, self._rbp.y + shift_point.y)
        self._rtp = Point(self._rtp.x + shift_point.x, self._rtp.y + shift_point.y)
        self._coords = Coords([self._lbp.list(), self._ltp.list(), self._rtp.list(), self._rbp.list()])

    # Сдвигает прямоугольник на величину shift по оси Х и возвращает параллельный прямоугольник
    def shift_given_angle(self, shift: int) -> Rectangle:
        shift_x = 0
        shift_y = 0

        # Вычисляем угол наклона в радианах
        angle_radians = np.radians(self.angle)

        # Определяем направление смещения в зависимости от выбранного направления
        if int(self.angle) < 45:
            shift_x = shift * np.cos(angle_radians)
            shift_y = shift * np.sin(angle_radians)

        elif int(self.angle) >= 45:
            shift_x = shift * np.sin(angle_radians)
            shift_y = -shift * np.cos(angle_radians)

        # Смещаем каждую точку прямоугольника на заданное расстояние
        rectangle_coords = self.coords.copy()

        # Смещаем каждую точку прямоугольника на заданное расстояние
        shifted_rectangle = []
        for point in rectangle_coords:
            shifted_point = [point[0] + shift_x, point[1] + shift_y]
            shifted_rectangle.append(shifted_point)

        shifted_contour = np.array(shifted_rectangle, dtype=np.int32)

        shifted_rectangle = Rectangle(shifted_contour, True)

        return shifted_rectangle

    # TODO: ПЕРЕДЕЛАТЬ. НЕ РАБОТАЕТ
    # Уменьшает на заданный процент
    def decrease(self, width_percent: float, height_percent: float) -> Rectangle:
        width_percent = round(self._width / 100 * width_percent)
        height_percent = round(self._height / 100 * height_percent)
        width_percent = round(self._width / 100 * width_percent)
        height_percent = round(self._height / 100 * height_percent)

        lbp = Point(self.lbp.x + width_percent, self.lbp.y - height_percent)
        ltp = Point(self.ltp.x + width_percent, self.ltp.y + height_percent)
        rtp = Point(self.rtp.x - width_percent, self.rtp.y + height_percent)
        rbp = Point(self.rbp.x - width_percent, self.rbp.y - height_percent)

        coords = Coords([lbp.list(), ltp.list(), rtp.list(), rbp.list()])
        contour = np.array(coords, dtype=np.int32)
        contour = contour.reshape((-1, 1, 2))

        return Rectangle(contour)
