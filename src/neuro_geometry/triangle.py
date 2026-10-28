""" Прямоугольный треугольник с вертикальным катетом (tp–bp). """

from __future__ import annotations

from typing import NamedTuple

from .point import Point


class Triangle(NamedTuple):
    """ Треугольник: bp — нижняя точка, tp — верхняя, lrp — левая или правая точка. """

    bp: Point
    tp: Point
    lrp: Point

    def lr_line_len(self) -> int:
        """ Длина левой/правой стороны (tp–bp). """
        return self.tp.distance_to(self.bp)

    def t_line_len(self) -> int:
        """ Длина верхней стороны (tp–lrp). """
        return self.tp.distance_to(self.lrp)

    def b_line_len(self) -> int:
        """ Длина нижней стороны (bp–lrp). """
        return self.bp.distance_to(self.lrp)
