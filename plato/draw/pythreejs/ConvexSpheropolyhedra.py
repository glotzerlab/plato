import numpy as np

from ... import draw
from ... import mesh
from .internal import ThreeJSPrimitive

class ConvexSpheropolyhedra(draw.ConvexSpheropolyhedra, ThreeJSPrimitive):
    __doc__ = draw.ConvexSpheropolyhedra.__doc__

    def update_arrays(self):
        if not self._dirty_attributes:
            return

        vertices = self.vertices
        if len(vertices) < 4:
            vertices = np.concatenate([vertices,
                [(-1, -1, -1), (1, 1, -1), (1, -1, 1), (-1, 1, 1)]], axis=0)

        gen_mesh = mesh.convexSpheropolyhedronMesh(vertices, self.radius)
        (positions, orientations, colors, images, normals) = mesh.unfoldProperties(
            [self.positions, self.orientations, self.colors],
            [gen_mesh.image, gen_mesh.normal])

        self._finalize_primitive_arrays(
            positions, orientations, colors, images, normals, gen_mesh.indices)
