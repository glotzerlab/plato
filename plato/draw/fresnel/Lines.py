import fresnel
import itertools
import numpy as np
from ... import draw
from ..internal import ShapeAttribute
from .FresnelPrimitive import FresnelPrimitive

class Lines(draw.Lines, FresnelPrimitive):
    __doc__ = draw.Lines.__doc__

    _ATTRIBUTES = draw.Lines._ATTRIBUTES

    _ATTRIBUTES.extend(list(itertools.starmap(ShapeAttribute, [
        ('outline', np.float32, 0, 0, False,
         'Outline width for all particles')
    ])))

    def __init__(self, *args, material=None, **kwargs):
        FresnelPrimitive.__init__(self, *args, material, **kwargs)
        if material is None:
            self._material.solid = 1
        draw.Lines.__init__(self, *args, **kwargs)

    def render(self, scene):
        geometry = fresnel.geometry.Cylinder(
            scene=scene,
            N=len(self.start_points),
            material=self._material)
        geometry.points[:, 0, :] = self.start_points
        geometry.points[:, 1, :] = self.end_points
        geometry.radius[:] = self.widths/2
        geometry.color[:, 0, :] = fresnel.color.linear(self.colors)
        geometry.color[:, 1, :] = fresnel.color.linear(self.colors)
        return geometry
