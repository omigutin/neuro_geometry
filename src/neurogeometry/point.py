from __future__ import annotations

from math import sqrt
from typing import Any


class Point(object):
    x: Any
    y: Any

    def __init__(self, x: Any | list | tuple, y: Any | list | tuple | None = None) -> None:
        if isinstance(x, list) or isinstance(x, tuple):
            self.x = x[0]
            self.y = x[1]
        else:
            if y is None:
                raise Exception("ERROR: class Point: If first arg is tuple or list, second arg must be not None.")
            self.x = x
            self.y = y

        if isinstance(self.x, float):
            self.x = round(self.x)
        else:
            try:
                self.x = int(self.x)
            except Exception as e:
                raise Exception("ERROR: class Point: Can't convert Point.x to int.")

        if isinstance(self.y, float):
            self.y = round(self.y)
        else:
            try:
                self.y = int(self.y)
            except Exception as e:
                raise Exception("ERROR: class Point: Can't convert Point.y to int.")

    def __add__(self, point: Point) -> Point:
        """(x1+x2, y1+y2)"""
        return Point(self.x + point.x, self.y + point.y)

    def __sub__(self, point: Point) -> Point:
        """(x1-x2, y1-y2)"""
        return Point(self.x - point.x, self.y - point.y)

    def distance_to(self, point: Point) -> int:
        return round(sqrt((self.x - point.x) ** 2 + (self.y - point.y) ** 2))

    def tuple(self) -> tuple:
        """(x, y)"""
        return self.x, self.y

    def list(self) -> list:
        """[x, y]"""
        return [self.x, self.y]
