import itertools

import fresnel
import numpy as np

from ... import draw
from ..internal import ShapeAttribute, ShapeDecorator
from .FresnelPrimitive import FresnelPrimitive

@ShapeDecorator
class ConvexPolyhedra(FresnelPrimitive, draw.ConvexPolyhedra):
    __doc__ = draw.ConvexPolyhedra.__doc__

    _ATTRIBUTES = draw.ConvexPolyhedra._ATTRIBUTES + list(
        itertools.starmap(ShapeAttribute, [
        ('outline', np.float32, 0, 0, False,
         'Outline width for all particles')
    ]))

    def render(self, scene):
        polyhedron_info = fresnel.util.convex_polyhedron_from_vertices(self.vertices)
        geometry = fresnel.geometry.ConvexPolyhedron(
            scene=scene,
            polyhedron_info=polyhedron_info,
            position=self.positions,
            orientation=self.orientations,
            color=fresnel.color.linear(self.colors),
            material=self._material,
            outline_width=self.outline)
        return geometry
