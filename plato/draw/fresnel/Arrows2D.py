import fresnel
from ... import draw
from .Polygons import Polygons
from .FresnelPrimitive import FresnelPrimitive

class Arrows2D(draw.Arrows2D, Polygons):
    __doc__ = draw.Arrows2D.__doc__

    def __init__(self, *args, material=None, **kwargs):
        FresnelPrimitive.__init__(self, *args, material, **kwargs)
        if material is None:
            self._material.solid = 1
        draw.Arrows2D.__init__(self, *args, **kwargs)
