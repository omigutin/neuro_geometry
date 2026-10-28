""" Четырёхугольник, заданный двумя диагональными точками или вершинами многоугольника. """

from __future__ import annotations

from ._polygon import shoelace_area
from .point import Point
from .types import Area, CoordsLike, Height, IntCoords, Width


class Quadrangle:
    """
    Четырёхугольник с углами lbp, ltp, rtp, rbp (левый нижний, левый верхний, правый верхний, правый нижний).

    Из 2 точек строится прямоугольник по осям (точки — противоположные углы).
    Из 3 и более точек выбираются крайние: точки делятся на левые и правые относительно центроида,
    в каждой группе берутся самая верхняя и самая нижняя.
    Ось Y направлена вниз (координаты изображения).
    """

    __slots__ = (
        "_area",
        "_bottom_width",
        "_coords",
        "_cp",
        "_lbp",
        "_left_height",
        "_ltp",
        "_max_height",
        "_max_width",
        "_min_height",
        "_min_width",
        "_rbp",
        "_right_height",
        "_rtp",
        "_top_width",
    )

    _coords: IntCoords  # упорядоченные координаты [lbp, ltp, rtp, rbp]
    _lbp: Point  # левая нижняя точка
    _ltp: Point  # левая верхняя точка
    _rtp: Point  # правая верхняя точка
    _rbp: Point  # правая нижняя точка
    _cp: Point  # центроид входных точек
    _min_height: Height
    _max_height: Height
    _min_width: Width
    _max_width: Width
    _bottom_width: Width
    _top_width: Width
    _left_height: Height
    _right_height: Height
    _area: Area

    def __init__(self, coords: CoordsLike) -> None:
        self._calculate_attributes(coords)

    def _calculate_attributes(self, coords: CoordsLike) -> None:
        """ Пересчитывает углы и все производные величины. """
        if len(coords) < 2:
            raise ValueError(f"Quadrangle requires at least 2 points, got {len(coords)}")

        self._cp = Quadrangle.centroid(coords)
        if len(coords) == 2:
            self.corners_from_two_points(coords)
        else:
            self.corners_from_four_points(coords)

        self._coords = [self._lbp.list(), self._ltp.list(), self._rtp.list(), self._rbp.list()]
        self._bottom_width = self._lbp.distance_to(self._rbp)
        self._top_width = self._ltp.distance_to(self._rtp)
        self._left_height = self._lbp.distance_to(self._ltp)
        self._right_height = self._rbp.distance_to(self._rtp)
        self._min_height = min(self._left_height, self._right_height)
        self._max_height = max(self._left_height, self._right_height)
        self._min_width = min(self._bottom_width, self._top_width)
        self._max_width = max(self._bottom_width, self._top_width)
        self._area = shoelace_area([self._lbp, self._ltp, self._rtp, self._rbp])

    def corners_from_two_points(self, coords: CoordsLike) -> None:
        """ Углы прямоугольника по осям из двух противоположных точек. """
        (x1, y1), (x2, y2) = coords
        left, right = min(x1, x2), max(x1, x2)
        top, bottom = min(y1, y2), max(y1, y2)
        self._ltp = Point(left, top)
        self._lbp = Point(left, bottom)
        self._rtp = Point(right, top)
        self._rbp = Point(right, bottom)

    def corners_from_four_points(self, coords: CoordsLike) -> None:
        """ Находит 4 крайних угла многоугольника (lbp, ltp, rtp, rbp). """
        # Центроид без округления: округлённый центр может оставить левую группу пустой
        center_x = sum(p[0] for p in coords) / len(coords)
        left_points = sorted((p for p in coords if p[0] < center_x), key=lambda p: p[1])
        right_points = sorted((p for p in coords if p[0] >= center_x), key=lambda p: p[1])
        if not left_points or not right_points:
            raise ValueError("Quadrangle is degenerate: all points have the same X")

        self._lbp = Point(left_points[-1][0], left_points[-1][1])
        self._ltp = Point(left_points[0][0], left_points[0][1])
        self._rtp = Point(right_points[0][0], right_points[0][1])
        self._rbp = Point(right_points[-1][0], right_points[-1][1])

    def decrease(self, width_percent: float, height_percent: float) -> None:
        """ Уменьшает четырёхугольник: каждая сторона сдвигается внутрь на процент от max_width/max_height. """
        self._calculate_attributes(self.get_decreased_coords(width_percent, height_percent))

    def get_decreased_coords(self, width_percent: float, height_percent: float) -> IntCoords:
        """ Координаты уменьшенного четырёхугольника без изменения текущего. """
        return self._resized_coords(-width_percent, -height_percent)

    def increase(self, width_percent: float, height_percent: float) -> None:
        """ Увеличивает четырёхугольник: каждая сторона сдвигается наружу на процент от max_width/max_height. """
        self._calculate_attributes(self.get_increased_coords(width_percent, height_percent))

    def get_increased_coords(self, width_percent: float, height_percent: float) -> IntCoords:
        """ Координаты увеличенного четырёхугольника без изменения текущего. """
        return self._resized_coords(width_percent, height_percent)

    def _resized_coords(self, width_percent: float, height_percent: float) -> IntCoords:
        """ Сдвигает углы наружу (положительный процент) или внутрь (отрицательный). """
        dx = round(self._max_width / 100 * width_percent)
        dy = round(self._max_height / 100 * height_percent)
        return [
            [self._lbp.x - dx, self._lbp.y + dy],
            [self._ltp.x - dx, self._ltp.y - dy],
            [self._rtp.x + dx, self._rtp.y - dy],
            [self._rbp.x + dx, self._rbp.y + dy],
        ]

    def shift(self, shift_point: Point) -> None:
        """ Сдвигает четырёхугольник на вектор shift_point. """
        self._calculate_attributes(self.get_shifted_coords(shift_point))

    def get_shifted_coords(self, shift_point: Point) -> IntCoords:
        """ Координаты сдвинутого четырёхугольника без изменения текущего. """
        return [(p + shift_point).list() for p in (self._lbp, self._ltp, self._rtp, self._rbp)]

    @staticmethod
    def centroid(coords: CoordsLike) -> Point:
        """ Среднее арифметическое точек, округлённое до int. """
        n = len(coords)
        return Point(sum(p[0] for p in coords) / n, sum(p[1] for p in coords) / n)

    @property
    def area(self) -> Area:
        """ Площадь по вершинам lbp, ltp, rtp, rbp. """
        return self._area

    @property
    def coords(self) -> IntCoords:
        """ [lbp, ltp, rtp, rbp] """
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
        """ Центроид точек, по которым построен четырёхугольник. """
        return self._cp

    @property
    def tcp(self) -> Point:
        """ Середина верхней стороны. """
        return Point(
            self._ltp.x + round((self._rtp.x - self._ltp.x) / 2),
            min(self._ltp.y, self._rtp.y) + round(abs(self._rtp.y - self._ltp.y) / 2),
        )

    @property
    def bcp(self) -> Point:
        """ Середина нижней стороны. """
        return Point(
            self._lbp.x + round((self._rbp.x - self._lbp.x) / 2),
            min(self._lbp.y, self._rbp.y) + round(abs(self._rbp.y - self._lbp.y) / 2),
        )

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
    def bottom_width(self) -> Width:
        return self._bottom_width

    @property
    def top_width(self) -> Width:
        return self._top_width

    @property
    def left_height(self) -> Height:
        return self._left_height

    @property
    def right_height(self) -> Height:
        return self._right_height
