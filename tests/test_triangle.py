from neuro_geometry import Point, Triangle


def test_side_lengths() -> None:
    triangle = Triangle(bp=Point(0, 40), tp=Point(0, 0), lrp=Point(30, 40))
    assert triangle.lr_line_len() == 40
    assert triangle.t_line_len() == 50
    assert triangle.b_line_len() == 30
