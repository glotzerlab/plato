import itertools

import numpy as np

from ... import draw
from ...geometry import fibonacciPositions
from ... import mesh
from .internal import ThreeJSPrimitive
from ..internal import ShapeAttribute, ShapeDecorator

@ShapeDecorator
class Spheres(draw.Spheres, ThreeJSPrimitive):
    __doc__ = draw.Spheres.__doc__

    _ATTRIBUTES = draw.Spheres._ATTRIBUTES + list(
        itertools.starmap(ShapeAttribute, [
        ('vertex_count', np.int32, 64, 0, False,
         'Number of vertices used to render sphere')
    ]))

    def update_arrays(self):
        if not self._dirty_attributes:
            return

        vertices = fibonacciPositions(self.vertex_count)

        (vertices, indices) = mesh.convexHull(vertices)
        (positions, colors, diameters, images) = mesh.unfoldProperties(
            [self.positions, self.colors, self.diameters],
            [vertices])

        images *= diameters

        # these are incorrect normals, but this looks to be the most
        # straightforward way to have the normals get serialized
        normals = images.copy()

        self._finalize_primitive_arrays(
            positions, None, colors, images, normals, indices)
