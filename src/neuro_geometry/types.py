""" Псевдонимы типов пакета. """

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeAlias

import numpy as np
import numpy.typing as npt

# Координаты на входе: последовательность пар [x, y] или массив numpy формы (N, 2) / (N, 1, 2)
CoordsLike: TypeAlias = Sequence[Sequence[float]] | npt.NDArray[np.generic]
# Координаты на выходе: список пар [x, y]
Coords: TypeAlias = list[list[float]]
# Массив вершин формы (N, 2), float64
FloatArray: TypeAlias = npt.NDArray[np.float64]
# Контур в формате OpenCV: (N, 1, 2), int32
CvContour: TypeAlias = npt.NDArray[np.int32]
