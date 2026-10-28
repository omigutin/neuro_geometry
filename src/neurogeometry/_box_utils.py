"""Adapted from production_counters `pc_operations.box_to_coords` (no OpenCV)."""

from __future__ import annotations

import numpy as np

from .point import Point
from .types import Coords


def box_to_coords(box: list, shift: Point | None = None) -> Coords:
    """
    list[x1, y1, x2, y2, ...] -> list[[x1, y1], [x2, y2], ...]
    Optional shift by Point (same semantics as monolith).
    """
    try:
        coords: Coords = np.array(box).reshape(-1, 2).tolist()
        if shift is not None:
            coords = [[x + shift.x, y + shift.y] for x, y in coords]
    except Exception as e:
        print(e)
        raise

    return coords


def contour_from_coords(coords: Coords) -> np.ndarray:
    """Same as `Contour.get_from_coords` in monolith (numpy only)."""
    contour = np.array(coords, dtype=np.int32)
    contour = contour.reshape((-1, 1, 2))
    return contour
