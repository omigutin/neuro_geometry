""" Внутренние утилиты для Rectangle. """

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import numpy.typing as npt

from .point import Point
from .types import Coords


def box_to_coords(box: Sequence[float] | Sequence[Sequence[float]], shift: Point | None = None) -> Coords:
    """ [x1, y1, x2, y2, ...] -> [[x1, y1], [x2, y2], ...], с необязательным сдвигом на точку. """
    flat = np.asarray(box).reshape(-1)
    if flat.size == 0 or flat.size % 2 != 0:
        raise ValueError(f"box must contain an even, non-zero number of values, got {flat.size}")
    coords: Coords = flat.reshape(-1, 2).tolist()
    if shift is not None:
        coords = [[x + shift.x, y + shift.y] for x, y in coords]
    return coords


def bounding_rect_xywh(points: npt.NDArray[np.generic]) -> tuple[int, int, int, int]:
    """
    Аналог `cv2.boundingRect` для набора точек: (x, y, w, h).
    Как и в OpenCV, границы включительные: w = xmax - xmin + 1.
    """
    pts = points.reshape(-1, 2)
    xmin, ymin = (int(v) for v in pts.min(axis=0))
    xmax, ymax = (int(v) for v in pts.max(axis=0))
    return xmin, ymin, xmax - xmin + 1, ymax - ymin + 1
