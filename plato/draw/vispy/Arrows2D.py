from ... import prims
from .internal import GLPrimitive, GLShapeDecorator
from .Polygons import Polygons

@GLShapeDecorator
class Arrows2D(prims.Arrows2D, Polygons):
    __doc__ = prims.Arrows2D.__doc__

    def __init__(self, *args, **kwargs):
        GLPrimitive.__init__(self)
        prims.Arrows2D.__init__(self, *args, **kwargs)
