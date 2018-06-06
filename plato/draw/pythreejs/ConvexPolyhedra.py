from ... import draw
from ... import math
from ... import mesh
from .internal import ThreeJSPrimitive
import numpy as np
import pythreejs

class ConvexPolyhedra(draw.ConvexPolyhedra, ThreeJSPrimitive):
    __doc__ = draw.ConvexPolyhedra.__doc__

    def update_arrays(self):
        if not self._dirty_attributes:
            return

        vertices = self.vertices
        if len(vertices) < 4:
            vertices = np.concatenate([vertices,
                [(-1, -1, -1), (1, 1, -1), (1, -1, 1), (-1, 1, 1)]], axis=0)

        (image, normal, indices, _) = mesh.convexPolyhedronMesh(vertices)
        (positions, orientations, colors, images, normals) = mesh.unfoldProperties(
            [self.positions, self.orientations, self.colors],
            [image, normal])

        self._finalize_primitive_arrays(
            positions, orientations, colors, images, normals, indices)
