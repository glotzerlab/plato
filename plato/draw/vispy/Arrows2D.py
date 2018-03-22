from ... import draw
from .internal import GLPrimitive, GLShapeDecorator
from .Polygons import Polygons

@GLShapeDecorator
class Arrows2D(draw.Arrows2D, Polygons):
    __doc__ = draw.Arrows2D.__doc__

    def __init__(self, *args, **kwargs):
        GLPrimitive.__init__(self)
        draw.Arrows2D.__init__(self, *args, **kwargs)
