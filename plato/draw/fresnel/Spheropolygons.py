import fresnel
import numpy as np
from ... import draw
from .FresnelPrimitive import FresnelPrimitive
import rowan

class Spheropolygons(draw.Spheropolygons, FresnelPrimitive):
    __doc__ = draw.Spheropolygons.__doc__

    def __init__(self, *args, material=None, **kwargs):
        FresnelPrimitive.__init__(self, *args, material, **kwargs)
        if material is None:
            self._material.solid = 1
        draw.Polygons.__init__(self, *args, **kwargs)

    def render(self, scene):
        geometry = fresnel.geometry.Polygon(
            scene=scene,
            vertices=self.vertices,
            position=self.positions,
            angle=rowan.geometry.angle(rowan.normalize(self.orientations)),
            color=fresnel.color.linear(self.colors),
            rounding_radius=self.radius,
            material=self._material,
            outline_width=self.outline)
        return geometry
