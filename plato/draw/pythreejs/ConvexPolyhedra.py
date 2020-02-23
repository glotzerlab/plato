import numpy as np

from ... import draw
from ... import mesh
from .internal import ThreeJSPrimitive

class ConvexPolyhedra(draw.ConvexPolyhedra, ThreeJSPrimitive):
    __doc__ = draw.ConvexPolyhedra.__doc__

    def update_arrays(self):
        if not self._dirty_attributes:
            return

        vertices = self.vertices
        if len(vertices) < 4:
            vertices = np.concatenate([vertices,
                [(-1, -1, -1), (1, 1, -1), (1, -1, 1), (-1, 1, 1)]], axis=0)

        poly_mesh = mesh.convexPolyhedronMesh(vertices)
        (positions, orientations, colors, images, normals) = mesh.unfoldProperties(
            [self.positions, self.orientations, self.colors],
            [poly_mesh.image, poly_mesh.normal])

        self._finalize_primitive_arrays(
            positions, orientations, colors, images, normals, poly_mesh.indices)
