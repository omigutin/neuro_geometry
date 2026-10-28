"""
Python port of OpenCV `rotatingCalipers` + `minAreaRect` logic
(`modules/imgproc/src/rotcalipers.cpp`), numpy-only.

Used to match `cv2.minAreaRect` / `cv2.boxPoints` without depending on OpenCV at runtime.
"""

from __future__ import annotations

import math
from typing import NamedTuple

import numpy as np


class RotatedRect(NamedTuple):
    center: tuple[float, float]
    size: tuple[float, float]  # (width, height) as returned by OpenCV Size2f
    angle_deg: float


CALIPERS_MINAREARECT = 1

# OpenCV angle search grid (degrees, step 0.1) for `calipers_output_to_opencv_rotated_rect`
# 0.05° steps — finer grid reduces int-round mismatches vs legacy `cv2.boxPoints`
_ANGLE_GRID_DEG = np.linspace(-180, 180, 7201, dtype=np.float32)
_ANGLE_GRID_RAD = np.radians(_ANGLE_GRID_DEG)
_SIN_HALF = (np.sin(_ANGLE_GRID_RAD) * 0.5).astype(np.float32)
_COS_HALF = (np.cos(_ANGLE_GRID_RAD) * 0.5).astype(np.float32)


def _rotate90_ccw(vx: float, vy: float) -> tuple[float, float]:
    return -vy, vx


def _rotate90_cw(vx: float, vy: float) -> tuple[float, float]:
    return vy, -vx


def _rotate180(vx: float, vy: float) -> tuple[float, float]:
    return -vx, -vy


def _first_vec_is_right(v1x: float, v1y: float, v2x: float, v2y: float) -> bool:
    tx, ty = _rotate90_cw(v1x, v1y)
    return tx * v2x + ty * v2y < 0


def _andrew_monotone_chain(pts: np.ndarray) -> np.ndarray:
    pts = np.unique(pts, axis=0)
    if len(pts) <= 1:
        return pts.astype(np.float64)

    pts = pts[np.lexsort((pts[:, 1], pts[:, 0]))]

    def cross(
        o: tuple[float, float], a: tuple[float, float], b: tuple[float, float]
    ) -> float:
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower: list[tuple[float, float]] = []
    for p in pts:
        px, py = float(p[0]), float(p[1])
        while len(lower) >= 2 and cross(lower[-2], lower[-1], (px, py)) <= 0:
            lower.pop()
        lower.append((px, py))

    upper: list[tuple[float, float]] = []
    for p in reversed(pts):
        px, py = float(p[0]), float(p[1])
        while len(upper) >= 2 and cross(upper[-2], upper[-1], (px, py)) <= 0:
            upper.pop()
        upper.append((px, py))

    hull = lower[:-1] + upper[:-1]
    return np.array(hull, dtype=np.float64)


def _convex_hull_ccw(points: np.ndarray) -> np.ndarray:
    """
    Same cyclic order as `cv2.convexHull(..., clockwise=False, returnPoints=True)`:
    Andrew's chain + rotate to start at lexicographically smallest (x, y).
    """
    hull = _andrew_monotone_chain(points.reshape(-1, 2))
    if len(hull) <= 1:
        return hull.astype(np.float32)

    hull_i = np.round(hull).astype(np.int32)
    tuples = [(int(r[0]), int(r[1])) for r in hull_i]
    mi = min(range(len(tuples)), key=lambda i: tuples[i])

    rotated = np.vstack([hull[mi:], hull[:mi]])
    return rotated.astype(np.float32)


def _rotating_calipers(points: np.ndarray, n: int, mode: int) -> np.ndarray:
    """Returns 6 floats: corner x,y then two edge vectors (vx,vy) each."""
    minarea = float(np.finfo(np.float32).max)
    max_dist = 0.0

    best_left_idx = 0
    best_bottom_idx = 0
    best_base_a = 1.0
    best_base_b = 0.0
    best_width = 0.0
    best_height = 0.0

    inv_vect_length = np.zeros(n, dtype=np.float64)
    vect = np.zeros((n, 2), dtype=np.float64)

    left = right = top = bottom = 0
    seq = [0, 0, 0, 0]

    pt0x, pt0y = float(points[0, 0]), float(points[0, 1])
    left_x = right_x = pt0x
    top_y = bottom_y = pt0y

    for i in range(n):
        if pt0x < left_x:
            left_x = pt0x
            left = i
        if pt0x > right_x:
            right_x = pt0x
            right = i
        if pt0y > top_y:
            top_y = pt0y
            top = i
        if pt0y < bottom_y:
            bottom_y = pt0y
            bottom = i

        j = (i + 1) % n
        ptx, pty = float(points[j, 0]), float(points[j, 1])
        dx = ptx - pt0x
        dy = pty - pt0y
        vect[i, 0] = dx
        vect[i, 1] = dy
        inv_vect_length[i] = 1.0 / math.sqrt(dx * dx + dy * dy)

        pt0x, pt0y = ptx, pty

    # convex hull orientation
    orientation = 0.0
    ax, ay = float(vect[n - 1, 0]), float(vect[n - 1, 1])
    for i in range(n):
        bx, by = float(vect[i, 0]), float(vect[i, 1])
        convexity = ax * by - ay * bx
        if convexity != 0:
            orientation = 1.0 if convexity > 0 else -1.0
            break
        ax, ay = bx, by

    if orientation == 0:
        raise ValueError("degenerate hull orientation in rotatingCalipers")

    base_a = orientation
    base_b = 0.0

    seq[0] = bottom
    seq[1] = right
    seq[2] = top
    seq[3] = left

    rot_vx = [0.0] * 4
    rot_vy = [0.0] * 4

    for _k in range(n):
        main_element = 0
        rot_vx[0] = float(vect[seq[0], 0])
        rot_vy[0] = float(vect[seq[0], 1])
        r1x, r1y = _rotate90_cw(float(vect[seq[1], 0]), float(vect[seq[1], 1]))
        rot_vx[1], rot_vy[1] = r1x, r1y
        r2x, r2y = _rotate180(float(vect[seq[2], 0]), float(vect[seq[2], 1]))
        rot_vx[2], rot_vy[2] = r2x, r2y
        r3x, r3y = _rotate90_ccw(float(vect[seq[3], 0]), float(vect[seq[3], 1]))
        rot_vx[3], rot_vy[3] = r3x, r3y

        for i in range(1, 4):
            if _first_vec_is_right(rot_vx[i], rot_vy[i], rot_vx[main_element], rot_vy[main_element]):
                main_element = i

        pindex = seq[main_element]
        lead_x = float(vect[pindex, 0]) * float(inv_vect_length[pindex])
        lead_y = float(vect[pindex, 1]) * float(inv_vect_length[pindex])

        if main_element == 0:
            base_a, base_b = lead_x, lead_y
        elif main_element == 1:
            base_a, base_b = lead_y, -lead_x
        elif main_element == 2:
            base_a, base_b = -lead_x, -lead_y
        elif main_element == 3:
            base_a, base_b = -lead_y, lead_x
        else:
            raise RuntimeError("main_element should be 0..3")

        seq[main_element] += 1
        if seq[main_element] == n:
            seq[main_element] = 0

        if mode == CALIPERS_MINAREARECT:
            dx = float(points[seq[1], 0]) - float(points[seq[3], 0])
            dy = float(points[seq[1], 1]) - float(points[seq[3], 1])
            width = dx * base_a + dy * base_b

            dx = float(points[seq[2], 0]) - float(points[seq[0], 0])
            dy = float(points[seq[2], 1]) - float(points[seq[0], 1])
            height = -dx * base_b + dy * base_a

            area = width * height
            if area <= minarea:
                minarea = area
                best_left_idx = seq[3]
                best_bottom_idx = seq[0]
                best_base_a = base_a
                best_base_b = base_b
                best_width = width
                best_height = height

    if mode == CALIPERS_MINAREARECT:
        A1 = best_base_a
        B1 = best_base_b
        A2 = -B1
        B2 = A1

        plx, ply = float(points[best_left_idx, 0]), float(points[best_left_idx, 1])
        pbx, pby = float(points[best_bottom_idx, 0]), float(points[best_bottom_idx, 1])

        C1 = A1 * plx + ply * B1
        C2 = A2 * pbx + pby * B2

        idet = 1.0 / (A1 * B2 - A2 * B1)
        px = (C1 * B2 - C2 * B1) * idet
        py = (A1 * C2 - A2 * C1) * idet

        out = np.zeros(6, dtype=np.float64)
        out[0] = px
        out[1] = py
        out[2] = A1 * best_width
        out[3] = B1 * best_width
        out[4] = A2 * best_height
        out[5] = B2 * best_height
        return out

    raise NotImplementedError("mode")


def rotated_rect_box_points(center: tuple[float, float], size: tuple[float, float], angle_deg: float) -> np.ndarray:
    """
    OpenCV `RotatedRect::points` (types.cpp), returns (4, 2) float32 — same order as `cv2.boxPoints`.
    """
    angle_rad = math.radians(angle_deg)
    b = math.cos(angle_rad) * 0.5
    a = math.sin(angle_rad) * 0.5
    cx, cy = center
    width, height = size[0], size[1]

    pts = np.empty((4, 2), dtype=np.float32)
    pts[0, 0] = cx - a * height - b * width
    pts[0, 1] = cy + b * height - a * width
    pts[1, 0] = cx + a * height - b * width
    pts[1, 1] = cy - b * height - a * width
    pts[2, 0] = 2 * cx - pts[0, 0]
    pts[2, 1] = 2 * cy - pts[0, 1]
    pts[3, 0] = 2 * cx - pts[1, 0]
    pts[3, 1] = 2 * cy - pts[1, 1]
    return pts


def calipers_output_to_opencv_rotated_rect(
    px: float, py: float, v1x: float, v1y: float, v2x: float, v2y: float
) -> RotatedRect:
    """
    The raw `rotatingCalipers` buffer encodes a rectangle, but `(width, height, angle)` may differ
    from OpenCV's canonical `cv2.minAreaRect` tuple while describing the same geometry.

    We recover OpenCV-compatible parameters by searching the angle so that `RotatedRect::points`
    matches the four parallelogram corners (integer-rounded corners must match legacy `cv2` path).
    """
    cx = px + (v1x + v2x) * 0.5
    cy = py + (v1y + v2y) * 0.5
    center = (float(cx), float(cy))

    n1 = float(math.hypot(v1x, v1y))
    n2 = float(math.hypot(v2x, v2y))
    if n1 <= 0 or n2 <= 0:
        return RotatedRect(center, (0.0, 0.0), 0.0)

    p0x, p0y = np.float32(px), np.float32(py)
    target = sorted(
        [
            (p0x, p0y),
            (p0x + np.float32(v1x), p0y + np.float32(v1y)),
            (p0x + np.float32(v1x + v2x), p0y + np.float32(v1y + v2y)),
            (p0x + np.float32(v2x), p0y + np.float32(v2y)),
        ]
    )

    best: tuple[tuple[float, float], tuple[float, float], float] | None = None
    best_score = float("inf")
    cx, cy = np.float32(center[0]), np.float32(center[1])
    target_arr = np.array(target, dtype=np.float32)

    for w, h in ((n1, n2), (n2, n1)):
        wf, hf = np.float32(w), np.float32(h)
        sh = _SIN_HALF
        ch = _COS_HALF
        p0x = cx - sh * hf - ch * wf
        p0y = cy + ch * hf - sh * wf
        p1x = cx + sh * hf - ch * wf
        p1y = cy - ch * hf - sh * wf
        p2x = np.float32(2) * cx - p0x
        p2y = np.float32(2) * cy - p0y
        p3x = np.float32(2) * cx - p1x
        p3y = np.float32(2) * cy - p1y
        stack = np.stack([p0x, p0y, p1x, p1y, p2x, p2y, p3x, p3y], axis=1)
        pts = stack.reshape(-1, 4, 2)
        for j in range(pts.shape[0]):
            row = pts[j]
            order = np.lexsort((row[:, 1], row[:, 0]))
            lex = row[order]
            score = float(np.abs(lex - target_arr).sum())
            if score < best_score:
                best_score = score
                best = ((float(cx), float(cy)), (float(wf), float(hf)), float(_ANGLE_GRID_DEG[j]))

    assert best is not None
    base_ang = best[2]
    base_c, base_wh = best[0], best[1]
    # refine angle ±0.15° in 0.01° steps (float32, matches cv2 rounding better)
    wf, hf = np.float32(base_wh[0]), np.float32(base_wh[1])
    cx, cy = np.float32(base_c[0]), np.float32(base_c[1])
    for delta in np.arange(-0.5, 0.501, 0.005, dtype=np.float64):
        ang = np.float32(base_ang + delta)
        rad = np.radians(ang, dtype=np.float32)
        b = np.cos(rad, dtype=np.float32) * np.float32(0.5)
        a = np.sin(rad, dtype=np.float32) * np.float32(0.5)
        bp0x = cx - a * hf - b * wf
        bp0y = cy + b * hf - a * wf
        bp1x = cx + a * hf - b * wf
        bp1y = cy - b * hf - a * wf
        bp2x = np.float32(2) * cx - bp0x
        bp2y = np.float32(2) * cy - bp0y
        bp3x = np.float32(2) * cx - bp1x
        bp3y = np.float32(2) * cy - bp1y
        row = np.stack(
            [[bp0x, bp0y], [bp1x, bp1y], [bp2x, bp2y], [bp3x, bp3y]], dtype=np.float32
        )
        order = np.lexsort((row[:, 1], row[:, 0]))
        lex = row[order]
        score = float(np.abs(lex - target_arr).sum())
        if score < best_score:
            best_score = score
            best = ((float(cx), float(cy)), (float(wf), float(hf)), float(ang))

    return RotatedRect(best[0], best[1], best[2])


def bounding_rect_xywh(contour: np.ndarray) -> tuple[int, int, int, int]:
    """
    Axis-aligned rect matching `cv2.boundingRect` for point sets (inclusive pixel extents).
    contour: (N, 1, 2) or (N, 2), int.
    """
    pts = contour.reshape(-1, 2)
    xmin = int(np.min(pts[:, 0]))
    ymin = int(np.min(pts[:, 1]))
    xmax = int(np.max(pts[:, 0]))
    ymax = int(np.max(pts[:, 1]))
    w = xmax - xmin + 1
    h = ymax - ymin + 1
    return xmin, ymin, w, h


def min_area_rect(points_xy: np.ndarray) -> RotatedRect:
    """
    `points_xy` shape (N, 2). Returns OpenCV-compatible RotatedRect (center, size, angle degrees).
    """
    hull = _convex_hull_ccw(points_xy)
    n = hull.shape[0]

    if n > 2:
        out = _rotating_calipers(hull, n, CALIPERS_MINAREARECT)
        px, py = out[0], out[1]
        v1x, v1y, v2x, v2y = out[2], out[3], out[4], out[5]
        return calipers_output_to_opencv_rotated_rect(px, py, v1x, v1y, v2x, v2y)

    if n == 2:
        h0 = hull[0]
        h1 = hull[1]
        cx = (float(h0[0]) + float(h1[0])) * 0.5
        cy = (float(h0[1]) + float(h1[1])) * 0.5
        dx = float(h1[0]) - float(h0[0])
        dy = float(h1[1]) - float(h0[1])
        seg_len = math.sqrt(dx * dx + dy * dy)
        ang = math.degrees(math.atan2(dy, dx))
        return RotatedRect((cx, cy), (seg_len, 0.0), ang)

    if n == 1:
        return RotatedRect((float(hull[0, 0]), float(hull[0, 1])), (0.0, 0.0), 0.0)

    return RotatedRect((0.0, 0.0), (0.0, 0.0), 0.0)
