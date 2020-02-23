import itertools

import fresnel
import numpy as np

from ... import draw
from ..internal import ShapeAttribute, ShapeDecorator
from .FresnelPrimitive import FresnelPrimitiveSolid

@ShapeDecorator
class Lines(FresnelPrimitiveSolid, draw.Lines):
    __doc__ = draw.Lines.__doc__

    _ATTRIBUTES = draw.Lines._ATTRIBUTES + list(
        itertools.starmap(ShapeAttribute, [
        ('outline', np.float32, 0, 0, False,
         'Outline width for all particles')
    ]))

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
