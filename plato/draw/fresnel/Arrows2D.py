from ... import draw
from .Polygons import Polygons

class Arrows2D(draw.Arrows2D, Polygons):
    __doc__ = draw.Arrows2D.__doc__

    def __init__(self, *args, **kwargs):
        draw.Arrows2D.__init__(self, *args, **kwargs)
