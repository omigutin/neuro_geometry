import numpy as np

from neuro_geometry import Line, Point, batch


def test_boxes() -> None:
    boxes = np.array([[0, 0, 10, 20], [5, 5, 1, 1]])
    assert batch.boxes_centers(boxes).tolist() == [[5, 10], [3, 3]]
    assert batch.boxes_areas(boxes).tolist() == [200, 16]


def test_shift_points_modes() -> None:
    pts = np.array([[0.0, 0.0], [1.0, 1.0]])
    new = batch.shift_points(pts, 1, 2)
    assert new is not pts and pts.tolist() == [[0, 0], [1, 1]] and new.tolist() == [[1, 2], [2, 3]]
    same = batch.shift_points(pts, 1, 2, out=pts)
    assert same is pts and pts.tolist() == [[1, 2], [2, 3]]
    target = np.empty_like(pts)
    assert batch.shift_points(pts, -1, -2, out=target) is target and target.tolist() == [[0, 0], [1, 1]]


def test_matches_scalar_line() -> None:
    rng = np.random.default_rng(0)
    a = rng.uniform(0, 100, size=(500, 2, 2))
    b = rng.uniform(0, 100, size=(500, 2, 2))
    got = batch.segments_intersections(a, b)
    for i in range(len(a)):
        expected = Line.from_coords(a[i]).intersection_with_segment(Line.from_coords(b[i]))
        if expected is None:
            assert np.isnan(got[i]).all()
        else:
            assert np.allclose(got[i], expected.to_tuple())

    pts = rng.uniform(0, 100, size=(100, 2))
    line = Line(10, 10, 90, 40)
    sides = batch.side_of_line(pts, [10, 10], [90, 40])
    assert np.allclose(sides, [line.side_of(Point(x, y)) for x, y in pts])


def test_crossed_line() -> None:
    line = [[0, 50], [100, 50]]
    prev = np.array([[10, 40], [10, 40], [200, 40], [50, 50]])
    cur = np.array([[10, 60], [20, 45], [200, 60], [60, 70]])
    assert batch.crossed_line(prev, cur, line).tolist() == [True, False, False, True]
