""" Округление координат до пикселей. """

from __future__ import annotations

import math
from typing import Any, TypeVar

import numpy as np
import numpy.typing as npt

from .types import CvContour

ArrayT = TypeVar("ArrayT", bound=np.ndarray[Any, Any])


def round_half_up(value: float) -> int:
    """ Округление половины вверх: 2.5 -> 3, -2.5 -> -2. В отличие от round(), без смещения к чётному. """
    return math.floor(value + 0.5)


def to_contour(points: npt.ArrayLike) -> CvContour:
    """ Вершины -> контур OpenCV (N, 1, 2) int32, координаты округляются половиной вверх. """
    arr = np.asarray(points, dtype=np.float64).reshape(-1, 2)
    contour: CvContour = np.floor(arr + 0.5).astype(np.int32).reshape(-1, 1, 2)
    return contour


def readonly(array: ArrayT) -> ArrayT:
    """ Представление массива только для чтения: без копирования данных. """
    view = array.view()
    view.flags.writeable = False
    return view
