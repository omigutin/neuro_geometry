""" Ленивый доступ к OpenCV: нужен только для повёрнутых прямоугольников. """

from __future__ import annotations

from types import ModuleType

import numpy as np

from .types import FloatArray


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


def min_area_rect(points: FloatArray) -> tuple[tuple[float, float], tuple[float, float], float]:
    """ cv2.minAreaRect: ((cx, cy), (w, h), angle_deg). """
    cv2 = _import_cv2()
    (cx, cy), (w, h), angle = cv2.minAreaRect(points.astype(np.float32))
    return (float(cx), float(cy)), (float(w), float(h)), float(angle)
