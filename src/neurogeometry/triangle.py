from typing import NamedTuple

from .point import Point


class Triangle(NamedTuple):
    bp: Point  # нижняя точка
    tp: Point  # верхняя точка
    lrp: Point  # левая/правая точка

    # длина левой/правой стороны
    def lr_line_len(self):
        return self.tp.distance_to(self.bp)

    # длина верхней стороны
    def t_line_len(self):
        return self.tp.distance_to(self.bp)

    # длина нижней стороны
    def b_line_len(self):
        return self.tp.distance_to(self.bp)
