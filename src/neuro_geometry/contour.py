""" Преобразование координат в контур формата OpenCV. """

from __future__ import annotations

import numpy as np

from .types import CoordsLike, CvContour


class Contour:
    """ Фабрика контуров формата OpenCV. """

    @staticmethod
    def get_from_coords(coords: CoordsLike) -> CvContour:
        """ [[x, y], ...] -> массив (N, 1, 2) int32. """
        return np.asarray(coords, dtype=np.int32).reshape((-1, 1, 2))
