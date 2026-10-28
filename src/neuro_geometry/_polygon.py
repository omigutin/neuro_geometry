""" Общие вычисления для многоугольников. """

from __future__ import annotations

from collections.abc import Sequence

from .point import Point


def shoelace_area(points: Sequence[Point]) -> float:
    """ Площадь простого многоугольника по формуле шнурования (вершины по порядку обхода). """
    n = len(points)
    twice_area = 0
    for i in range(n):
        a, b = points[i], points[(i + 1) % n]
        twice_area += a.x * b.y - b.x * a.y
    return abs(twice_area) / 2
