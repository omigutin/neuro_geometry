from __future__ import annotations

import numpy as np

from .types import Coords, CvContour


class Contour:
    # Преобразует список координат в контур
    @staticmethod
    def get_from_coords(coords: Coords) -> CvContour:
        contour = np.array(coords, dtype=np.int32)
        contour = contour.reshape((-1, 1, 2))
        return contour
