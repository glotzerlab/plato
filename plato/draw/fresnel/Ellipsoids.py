import itertools

import fresnel
import numpy as np

from ... import draw
from ...geometry import fibonacciPositions
from ..internal import ShapeAttribute, ShapeDecorator
from .FresnelPrimitive import FresnelPrimitive

@ShapeDecorator
class Ellipsoids(FresnelPrimitive, draw.Ellipsoids):
    __doc__ = draw.Ellipsoids.__doc__

    _ATTRIBUTES = draw.Ellipsoids._ATTRIBUTES + list(
        itertools.starmap(ShapeAttribute, [
        ('outline', np.float32, 0, 0, False,
         'Outline width for all particles'),
        ('vertex_count', np.int32, 256, 0, False,
         'Number of vertices used to render ellipsoid')
    ]))

    def render(self, scene):
        vertices = fibonacciPositions(self.vertex_count, self.a, self.b, self.c)
        polyhedron_info = fresnel.util.convex_polyhedron_from_vertices(vertices)
        geometry = fresnel.geometry.ConvexPolyhedron(
            scene=scene,
            polyhedron_info=polyhedron_info,
            position=self.positions,
            orientation=self.orientations,
            color=fresnel.color.linear(self.colors),
            material=self._material,
            outline_width=self.outline)
        return geometry
