""" 2D-геометрия для пайплайнов компьютерного зрения. """

from . import batch
from ._rounding import round_half_up, to_contour
from .line import Line, LineDirection
from .point import Point
from .quadrangle import Quadrangle
from .rectangle import Rectangle
from .triangle import Triangle

__all__ = [
    "Line",
    "LineDirection",
    "Point",
    "Quadrangle",
    "Rectangle",
    "Triangle",
    "batch",
    "round_half_up",
    "to_contour",
]
__version__ = "0.2.0"
