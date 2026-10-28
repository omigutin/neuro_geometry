""" Псевдонимы типов, совместимые с `pc_common.types.simple_type` из production_counters. """

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeAlias

import numpy as np
import numpy.typing as npt

Angle: TypeAlias = float
Area: TypeAlias = float
# Список пар [x, y]
Coords: TypeAlias = list[list[float]]
# Координаты на входе: любая последовательность пар [x, y]
CoordsLike: TypeAlias = Sequence[Sequence[float]]
# Координаты на выходе: вершины с целочисленными координатами
IntCoords: TypeAlias = list[list[int]]
# Контур в формате OpenCV: массив формы (N, 1, 2), dtype int32
CvContour: TypeAlias = npt.NDArray[np.int32]
Distance: TypeAlias = int
Height: TypeAlias = int
Width: TypeAlias = int
