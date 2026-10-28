"""
Векторные операции над массивами фигур — для обработки многих объектов кадра одним вызовом numpy.

Форматы: точки — (N, 2); боксы — (N, 4) как [x1, y1, x2, y2]; отрезки — (N, 2, 2) как [[x1, y1], [x2, y2]].
Одиночный отрезок (2, 2) или точка (2,) транслируются на все N (broadcasting).
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

from .types import FloatArray

__all__ = [
    "boxes_areas",
    "boxes_centers",
    "crossed_line",
    "segments_intersections",
    "shift_points",
    "side_of_line",
]

_SEGMENT_EPS = 1e-9
BoolArray = npt.NDArray[np.bool_]


def _as_float(array: npt.ArrayLike) -> FloatArray:
    return np.asarray(array, dtype=np.float64)


def boxes_centers(boxes: npt.ArrayLike) -> FloatArray:
    """ Центры боксов: (N, 4) -> (N, 2). """
    b = _as_float(boxes).reshape(-1, 4)
    return (b[:, :2] + b[:, 2:]) / 2


def boxes_areas(boxes: npt.ArrayLike) -> FloatArray:
    """ Площади боксов: (N, 4) -> (N,). """
    b = _as_float(boxes).reshape(-1, 4)
    return np.abs((b[:, 2] - b[:, 0]) * (b[:, 3] - b[:, 1]))


def shift_points(points: FloatArray, dx: float, dy: float, *, out: FloatArray | None = None) -> FloatArray:
    """
    Сдвиг точек (..., 2) на (dx, dy).
    out=None — новый массив; out=points — на месте без выделения памяти; иначе результат пишется в out.
    """
    if out is None:
        out = np.array(points, dtype=np.float64)
    elif out is not points:
        np.copyto(out, points)
    out[..., 0] += dx
    out[..., 1] += dy
    return out


def side_of_line(points: npt.ArrayLike, start: npt.ArrayLike, end: npt.ArrayLike) -> FloatArray:
    """
    Векторное произведение (end - start) x (point - start) для каждой точки: (N, 2) -> (N,).
    > 0 — справа от направления start -> end (на изображении), < 0 — слева, 0 — на прямой.
    """
    p, s, e = _as_float(points), _as_float(start), _as_float(end)
    return (e[..., 0] - s[..., 0]) * (p[..., 1] - s[..., 1]) - (e[..., 1] - s[..., 1]) * (p[..., 0] - s[..., 0])


def _segments_params(a: FloatArray, b: FloatArray) -> tuple[FloatArray, FloatArray, BoolArray]:
    """ Параметры t, u пересечения отрезков a и b и маска пересечения (концы включительно). """
    p1, d1 = a[..., 0, :], a[..., 1, :] - a[..., 0, :]
    p3, d2 = b[..., 0, :], b[..., 1, :] - b[..., 0, :]
    o = p3 - p1
    denominator = d1[..., 0] * d2[..., 1] - d1[..., 1] * d2[..., 0]
    with np.errstate(divide="ignore", invalid="ignore"):
        t = (o[..., 0] * d2[..., 1] - o[..., 1] * d2[..., 0]) / denominator
        u = (o[..., 0] * d1[..., 1] - o[..., 1] * d1[..., 0]) / denominator
    lo, hi = -_SEGMENT_EPS, 1 + _SEGMENT_EPS
    mask = (denominator != 0) & (t >= lo) & (t <= hi) & (u >= lo) & (u <= hi)
    return t, u, mask


def segments_intersections(a: npt.ArrayLike, b: npt.ArrayLike) -> FloatArray:
    """ Точки пересечения отрезков a[i] и b[i]: (N, 2, 2) x (N, 2, 2) -> (N, 2); NaN, если не пересекаются. """
    sa, sb = _as_float(a), _as_float(b)
    t, _, mask = _segments_params(sa, sb)
    points = sa[..., 0, :] + t[..., None] * (sa[..., 1, :] - sa[..., 0, :])
    points[~mask] = np.nan
    return points


def crossed_line(prev_points: npt.ArrayLike, cur_points: npt.ArrayLike, line: npt.ArrayLike) -> BoolArray:
    """
    Пересекло ли перемещение prev -> cur отрезок line: (N, 2), (N, 2), (2, 2) -> (N,) bool.
    Типовая проверка линии подсчёта для траекторий трекера.
    """
    moves = np.stack([_as_float(prev_points), _as_float(cur_points)], axis=-2)
    _, _, mask = _segments_params(moves, _as_float(line))
    return mask
