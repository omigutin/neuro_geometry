"""Type aliases compatible with production_counters `pc_common.types.simple_type`."""

from __future__ import annotations

from typing import TypeAlias

import numpy as np

Angle: TypeAlias = float
Area: TypeAlias = float
# Same semantic alias as in monolith: list of [x, y] pairs
Coords: TypeAlias = list[list[float]]
CvContour: TypeAlias = np.ndarray
Distance: TypeAlias = int
Height: TypeAlias = int
Width: TypeAlias = int
