""" 2D-геометрия для пайплайнов компьютерного зрения. """

from .contour import Contour
from .line import Line, LineDirection
from .point import Point
from .quadrangle import Quadrangle
from .rectangle import Rectangle
from .triangle import Triangle

__all__ = ["Contour", "Line", "LineDirection", "Point", "Quadrangle", "Rectangle", "Triangle"]
__version__ = "0.2.0"
