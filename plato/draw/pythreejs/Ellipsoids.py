import itertools

import numpy as np

from ... import draw
from ...geometry import fibonacciPositions
from ... import mesh
from .internal import ThreeJSPrimitive
from ..internal import ShapeAttribute, ShapeDecorator

@ShapeDecorator
class Ellipsoids(draw.Ellipsoids, ThreeJSPrimitive):
    __doc__ = draw.Ellipsoids.__doc__

    _ATTRIBUTES = draw.Ellipsoids._ATTRIBUTES + list(
        itertools.starmap(ShapeAttribute, [
        ('vertex_count', np.int32, 64, 0, False,
         'Number of vertices used to render ellipsoid')
    ]))

    def update_arrays(self):
        if not self._dirty_attributes:
            return

        vertices = fibonacciPositions(self.vertex_count, self.a, self.b, self.c)

        (vertices, indices) = mesh.convexHull(vertices)
        (positions, orientations, colors, images) = mesh.unfoldProperties(
            [self.positions, self.orientations, self.colors],
            [vertices])

        # these are incorrect normals, but this looks to be the most
        # straightforward way to have the normals get serialized
        normals = images.copy()

        self._finalize_primitive_arrays(
            positions, orientations, colors, images, normals, indices)
