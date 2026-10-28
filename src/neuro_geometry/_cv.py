""" Ленивый доступ к OpenCV: нужен только для повёрнутых прямоугольников. """

from __future__ import annotations

from types import ModuleType
from typing import TypeAlias

import numpy as np
import numpy.typing as npt

# ((cx, cy), (w, h), angle) — формат cv2.minAreaRect
RotatedRect: TypeAlias = tuple[tuple[float, float], tuple[float, float], float]


def _import_cv2() -> ModuleType:
    """ Импортирует cv2 или сообщает, как его установить. """
    try:
        import cv2
    except ImportError as e:
        raise ImportError(
            "OpenCV is required for rotated rectangles. "
            "Install it with `pip install neuro-geometry[cv]` or any opencv-python distribution."
        ) from e
    return cv2


def min_area_rect(points: npt.NDArray[np.generic]) -> tuple[RotatedRect, npt.NDArray[np.float32]]:
    """ cv2.minAreaRect + cv2.boxPoints: (rotated_rect, 4 угла формы (4, 2)). """
    cv2 = _import_cv2()
    pts = points.reshape(-1, 2)
    # cv2.minAreaRect принимает только int32 и float32
    pts = pts.astype(np.int32) if np.issubdtype(pts.dtype, np.integer) else pts.astype(np.float32)
    rect = cv2.minAreaRect(pts)
    (cx, cy), (w, h), angle = rect
    box = cv2.boxPoints(rect)
    return ((float(cx), float(cy)), (float(w), float(h)), float(angle)), box
