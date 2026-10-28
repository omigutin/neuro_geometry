__all__ = ["LineDirection", "Line"]

import math
from enum import Enum
from typing import Optional

import numpy as np

from .point import Point
from .types import Coords


# КОНСТАНТЫ направления линии
class LineDirection(Enum):
    NONE = 0
    VERTICAL = 1
    HORIZONTAL = 2


class Line(object):
    def __init__(self, coords: Coords) -> None:
        self.bp: Point | None = None
        self.tp: Point | None = None
        self.cp: Point | None = None
        self.lp: Point | None = None
        self.rp: Point | None = None
        self.length: int | None = None
        self.direction: LineDirection = LineDirection.NONE

        if len(coords) != 2:
            raise Exception("ERROR: Line should have 2 points.")

        # Копия точек: не мутировать список вызывающего кода (например Shape.coords).
        pts: Coords = [list(coords[0]), list(coords[1])]

        # Вычисляем изменение по координатам
        delta_x = abs(pts[0][0] - pts[1][0])
        delta_y = abs(pts[0][1] - pts[1][1])
        # Вычисляем угол наклона в градусах
        angle = math.degrees(math.atan2(delta_y, delta_x))
        # Приводим угол к диапазону [0, 180]
        angle = abs(angle) % 180
        # Определяем направление линии
        self.direction = LineDirection.HORIZONTAL if angle <= 45 else LineDirection.VERTICAL

        if self.direction == LineDirection.VERTICAL:
            # Сортируем по Y
            pts.sort(key=lambda p: p[1])
            self.bp = Point(pts[1][0], pts[1][1])
            self.tp = Point(pts[0][0], pts[0][1])
        else:
            # Сортируем по X
            pts.sort(key=lambda p: p[0])
            self.lp = Point(pts[0][0], pts[0][1])
            self.rp = Point(pts[1][0], pts[1][1])

        self.coords = pts

        self.cp = Point(
            (self.bp.x + self.tp.x) / 2 if self.direction == LineDirection.VERTICAL else (self.lp.x + self.rp.x) / 2,
            (self.bp.y + self.tp.y) / 2 if self.direction == LineDirection.VERTICAL else (self.lp.y + self.rp.y) / 2,
        )
        self.length = self.bp.distance_to(self.tp) if self.direction == LineDirection.VERTICAL else self.lp.distance_to(
            self.rp
        )

    def get_x_on_line(self, point: Point) -> int:
        # Проверяем, не является ли линия горизонтальной
        if self.tp.y == self.bp.y:
            raise ValueError("Линия горизонтальная, X не может быть определен для заданного Y.")
        # Вычисляем угловой коэффициент m
        m = (self.bp.y - self.tp.y) / (self.bp.x - self.tp.x)
        # Вычисляем свободный член b
        b = self.tp.y - m * self.tp.x
        # Находим x на линии для y = yp
        x_on_line = (point.y - b) / m
        return x_on_line

    def get_y_on_line(self, point: Point) -> float:
        # Проверяем, не является ли линия вертикальной
        if self.lp.x == self.rp.x:
            raise ValueError("Линия вертикальная, Y не может быть определен для заданного X.")
        # Вычисляем угловой коэффициент m
        m = (self.lp.y - self.rp.y) / (self.lp.x - self.rp.x)
        # Вычисляем свободный член b
        b = self.lp.y - m * self.lp.x
        # Находим Y на линии для заданного X
        y_on_line = m * point.x + b
        return y_on_line

    # Возвращает линию в виде списка кортежей (x, y)
    def list_of_tuples(self):
        return [self.tp.tuple(), self.bp.tuple()]

    def get_intersection_point_with_line(self, line2) -> Optional[Point]:
        """Вычисляет точку пересечения с линией"""
        x1, y1 = self.coords[0]
        x2, y2 = self.coords[1]
        x3, y3 = line2.coords[0]
        x4, y4 = line2.coords[1]

        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denominator == 0:
            return None  # Линии параллельны или совпадают, нет точки пересечения
        intersection_x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denominator
        intersection_y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denominator

        return Point(intersection_x, intersection_y)

    def get_intersection_point_with_line_segment(self, line_or_points) -> Optional[Point]:
        """Вычисляет точку пересечения с отрезком"""
        # Проверяем, является ли line_or_points экземпляром класса Line
        if isinstance(line_or_points, Line):
            line2 = line_or_points
            p1 = np.array(self.coords[0])  # Начало первого отрезка
            p2 = np.array(self.coords[1])  # Конец первого отрезка
            p3 = np.array(line2.coords[0])  # Начало второго отрезка
            p4 = np.array(line2.coords[1])  # Конец второго отрезка
        else:
            # Если это две точки, извлекаем координаты
            point1, point2 = line_or_points
            p1 = np.array([point1.x, point1.y])  # Начало первого отрезка
            p2 = np.array([point2.x, point2.y])  # Конец первого отрезка
            p3 = np.array(self.coords[0])  # Начало второго отрезка
            p4 = np.array(self.coords[1])  # Конец второго отрезка
        # Векторные представления отрезков
        d1 = p2 - p1  # Вектор первого отрезка
        d2 = p4 - p3  # Вектор второго отрезка
        # Определяем матрицу коэффициентов
        denominator = d1[0] * d2[1] - d1[1] * d2[0]
        if denominator == 0:
            return None  # Линии параллельны или совпадают, нет точки пересечения
        # Вычисляем параметры t и u
        t = ((p3[0] - p1[0]) * d2[1] - (p3[1] - p1[1]) * d2[0]) / denominator
        u = ((p3[0] - p1[0]) * d1[1] - (p3[1] - p1[1]) * d1[0]) / denominator
        # Проверяем, находится ли точка пересечения на обоих отрезках
        if 0 <= t <= 1 and 0 <= u <= 1:
            intersection_point = p1 + t * d1  # Вычисляем точку пересечения
            return Point(intersection_point[0], intersection_point[1])
        return None  # Точка пересечения не лежит на отрезках

    # Возвращает длину линии
    def __len__(self):
        return self.tp.distance_to(self.bp)
