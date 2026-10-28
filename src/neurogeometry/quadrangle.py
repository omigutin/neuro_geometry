from typing import Optional

from .point import Point
from .types import Area, Coords, Height, Width


class Quadrangle(object):
    __slots__ = (
        "_coords",
        "_lbp",
        "_ltp",
        "_rtp",
        "_rbp",
        "_cp",
        "_min_height",
        "_max_height",
        "_min_width",
        "_max_width",
        "_bottom_width",
        "_top_width",
        "_left_height",
        "_right_height",
        "_area",
    )

    def __init__(self, coords: Coords):
        self._coords: Optional[Coords] = None  # упорядоченные координаты
        self._lbp: Optional[Point] = None  # левая нижняя точка
        self._ltp: Optional[Point] = None  # левая верхняя точка
        self._rtp: Optional[Point] = None  # правая верхняя точка
        self._rbp: Optional[Point] = None  # правая нижняя точка
        self._cp: Optional[Point] = None  # центральная точка
        self._min_height: Optional[Height] = None  # наименьшая высота
        self._max_height: Optional[Height] = None  # наибольшая высота
        self._min_width: Optional[Width] = None  # наименьшая ширина
        self._max_width: Optional[Width] = None  # наибольшая ширина
        self._bottom_width: Optional[Width] = None  # нижняя ширина
        self._top_width: Optional[Width] = None  # верхняя ширина
        self._left_height: Optional[Height] = None  # левая высота
        self._right_height: Optional[Height] = None  # правая высота
        self._area: Optional[Area] = None  # площадь

        self._calculate_attributes(coords)

    def _calculate_attributes(self, coords: Coords) -> None:
        self._cp = Quadrangle.centroid(coords)
        # Прямоугольник
        if len(coords) == 2:
            self.corners_from_two_points(coords)
        # Четырёхугольник
        else:
            self.corners_from_four_points(coords)
        self._coords = Coords([self._lbp.list(), self._ltp.list(), self._rtp.list(), self._rbp.list()])
        self._min_height = min(self._lbp.distance_to(self._ltp), self._rbp.distance_to(self._rtp))
        self._min_width = min(self._lbp.distance_to(self._rbp), self._ltp.distance_to(self._rtp))
        self._max_height = max(self._lbp.distance_to(self._ltp), self._rbp.distance_to(self._rtp))
        self._max_width = max(self._lbp.distance_to(self._rbp), self._ltp.distance_to(self._rtp))
        self._bottom_width = self._lbp.distance_to(self._rbp)
        self._top_width = self._ltp.distance_to(self._rtp)
        self._left_height = self._lbp.distance_to(self._ltp)
        self._right_height = self._rbp.distance_to(self._rtp)
        self._area = self._get_area()

    def corners_from_two_points(self, coords) -> None:
        # левая точка
        if coords[0][0] < self._cp.x:
            # верхняя точка
            if coords[0][1] < self._cp.y:
                self._ltp = Point(coords[0][0], coords[0][1])
                self._rbp = Point(coords[1][0], coords[1][1])
                self._lbp = Point(self._ltp.x, self._rbp.y)
                self._rtp = Point(self._rbp.x, self._ltp.y)
            # нижняя точка
            else:
                self._lbp = Point(coords[0][0], coords[0][1])
                self._rtp = Point(coords[1][0], coords[1][1])
                self._ltp = Point(self._lbp.x, self._rtp.y)
                self._rbp = Point(self._rtp.x, self._lbp.y)
        # правая точка
        else:
            # верхняя точка
            if coords[0][1] < self._cp.y:
                self._rtp = Point(coords[0][0], coords[0][1])
                self._lbp = Point(coords[1][0], coords[1][1])
                self._ltp = Point(self._lbp.x, self._rtp.y)
                self._rbp = Point(self._rtp.x, self._lbp.y)
            # нижняя точка
            else:
                self._rbp = Point(coords[0][0], coords[0][1])
                self._ltp = Point(coords[1][0], coords[1][1])
                self._lbp = Point(self._ltp.x, self._rbp.y)
                self._rtp = Point(self._rbp.x, self._ltp.y)

    # Находит 4 крайние угла многоугольника (lbp, ltp, rtp, rbp)
    def corners_from_four_points(self, coords: Coords) -> None:
        left_points = list()
        right_points = list()
        for dot in coords:
            if dot[0] < self._cp.x:
                left_points.append(dot)
            else:
                right_points.append(dot)

        left_points.sort(key=lambda p: p[1])
        right_points.sort(key=lambda p: p[1])

        self._lbp = Point(left_points[-1][0], left_points[-1][1])
        self._ltp = Point(left_points[0][0], left_points[0][1])
        self._rtp = Point(right_points[0][0], right_points[0][1])
        self._rbp = Point(right_points[-1][0], right_points[-1][1])

    # Вычисляет площадь четырёхугольника
    def _get_area(self) -> Area:
        half_perimeter = 0.5 * (self._left_height + self._top_width + self._right_height + self._bottom_width)
        area = (half_perimeter - self._left_height) * (half_perimeter - self._top_width) * (
            half_perimeter - self._right_height
        ) * (half_perimeter - self._bottom_width)
        area = pow(area, 0.5)
        return area

    # Уменьшает четырехугольник на заданный процент
    def decrease(self, width_percent: float, height_percent: float) -> None:
        coords = self.get_decreased_coords(width_percent, height_percent)
        self._calculate_attributes(coords)

    def get_decreased_coords(self, width_percent: float, height_percent: float) -> Coords:
        width_shift = round(self.max_width / 100 * width_percent)
        height_shift = round(self.max_height / 100 * height_percent)
        lbp = Point(self.lbp.x + width_shift, self.lbp.y - height_shift)
        ltp = Point(self.ltp.x + width_shift, self.ltp.y + height_shift)
        rtp = Point(self.rtp.x - width_shift, self.rtp.y + height_shift)
        rbp = Point(self.rbp.x - width_shift, self.rbp.y - height_shift)
        return Coords([lbp.list(), ltp.list(), rtp.list(), rbp.list()])

    # Увеличивает четырехугольник на заданный процент
    def increase(self, width_percent: float, height_percent: float) -> None:
        coords = self.get_increased_coords(width_percent, height_percent)
        self._calculate_attributes(coords)

    def get_increased_coords(self, width_percent: float, height_percent: float) -> Coords:
        width_shift = round(self.max_width / 100 * width_percent)
        height_shift = round(self.max_height / 100 * height_percent)
        lbp = Point(self.lbp.x - width_shift, self.lbp.y + height_shift)
        ltp = Point(self.ltp.x - width_shift, self.ltp.y - height_shift)
        rtp = Point(self.rtp.x + width_shift, self.rtp.y - height_shift)
        rbp = Point(self.rbp.x + width_shift, self.rbp.y + height_shift)
        return Coords([lbp.list(), ltp.list(), rtp.list(), rbp.list()])

    # Сдвигает углы четырехугольника на заданную точку
    def shift(self, shift_point: Point) -> None:
        coords = self.get_shifted_coords(shift_point)
        self._calculate_attributes(coords)

    def get_shifted_coords(self, shift_point: Point) -> Coords:
        lbp = Point(self._lbp.x + shift_point.x, self._lbp.y + shift_point.y)
        ltp = Point(self._ltp.x + shift_point.x, self._ltp.y + shift_point.y)
        rbp = Point(self._rbp.x + shift_point.x, self._rbp.y + shift_point.y)
        rtp = Point(self._rtp.x + shift_point.x, self._rtp.y + shift_point.y)
        return Coords([lbp.list(), ltp.list(), rtp.list(), rbp.list()])

    # Находит середину многоугольника
    @staticmethod
    def centroid(coords: Coords) -> Point:
        x = 0
        y = 0

        for dot in coords:
            x = x + dot[0]
            y = y + dot[1]
        x = x / len(coords)
        y = y / len(coords)

        return Point(x, y)

    @property
    def area(self) -> Area:
        return self._area

    @property
    def coords(self) -> Coords:
        return self._coords

    @property
    def lbp(self) -> Point:
        return self._lbp

    @property
    def ltp(self) -> Point:
        return self._ltp

    @property
    def rtp(self) -> Point:
        return self._rtp

    @property
    def rbp(self) -> Point:
        return self._rbp

    @property
    def cp(self) -> Point:
        return self._cp

    @property
    def tcp(self) -> Point:
        x = self._ltp.x + round((self._rtp.x - self._ltp.x) / 2)
        if self._rtp.y > self._ltp.y:
            y = self._ltp.y + round((self._rtp.y - self._ltp.y) / 2)
        else:
            y = self._rtp.y + round((self._ltp.y - self._rtp.y) / 2)
        return Point(x, y)

    @property
    def bcp(self) -> Point:
        x = self._lbp.x + round((self._rbp.x - self._lbp.x) / 2)
        if self._rbp.y > self._lbp.y:
            y = self._lbp.y + round((self._rbp.y - self._lbp.y) / 2)
        else:
            y = self._rbp.y + round((self._lbp.y - self._rbp.y) / 2)
        return Point(x, y)

    @property
    def min_height(self) -> Height:
        return self._min_height

    @property
    def max_height(self) -> Height:
        return self._max_height

    @property
    def min_width(self) -> Width:
        return self._min_width

    @property
    def max_width(self) -> Width:
        return self._max_width

    @property
    def bottom_width(self):
        return self._bottom_width

    @property
    def top_width(self):
        return self._top_width

    @property
    def left_height(self):
        return self._left_height

    @property
    def right_height(self):
        return self._right_height
