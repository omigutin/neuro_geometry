"""Smoke: пакет импортируется после editable install."""


def test_import_neurogeometry():
    from neurogeometry import Line, LineDirection, Point, Quadrangle, Rectangle, Triangle

    assert Point(1, 2).tuple() == (1, 2)
    assert LineDirection.HORIZONTAL.value == 2
    assert all(c is not None for c in (Line, Quadrangle, Rectangle, Triangle))


def test_line_does_not_mutate_caller_coords():
    """Line сортирует внутреннюю копию; исходный список точек не меняется."""
    from neurogeometry import Line

    original = [[100, 50], [0, 50]]
    snapshot = [row[:] for row in original]
    Line(original)
    assert original == snapshot
