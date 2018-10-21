import fresnel
from ... import draw
from .Polygons import Polygons

class Arrows2D(draw.Arrows2D, Polygons):
    __doc__ = draw.Arrows2D.__doc__

    def __init__(self, *args, material=None, **kwargs):
        if material is None:
            self._material = fresnel.material.Material(primitive_color_mix=1)
            self._material.solid = 1
        else:
            self._material = material
        draw.Arrows2D.__init__(self, *args, **kwargs)
