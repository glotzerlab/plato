import numpy as np

from ... import draw
from ... import mesh
from .internal import ThreeJSPrimitive

class Mesh(draw.Mesh, ThreeJSPrimitive):
    __doc__ = draw.Mesh.__doc__

    def update_arrays(self):
        if not self._dirty_attributes:
            return

        normals = mesh.computeNormals_(self.vertices, self.indices)

        vertex_colors = self.colors
        if len(vertex_colors) < len(self.vertices):
            vertex_colors = np.tile(
                vertex_colors, (len(self.vertices)//len(vertex_colors), 1))

        shape_colors = self.shape_colors
        if len(shape_colors) < len(self.positions):
            shape_colors = np.tile(
                shape_colors, (len(self.positions)//len(shape_colors), 1))

        (positions, orientations, shape_colors, images, normals, vertex_colors) = mesh.unfoldProperties(
            [self.positions, self.orientations, shape_colors],
            [self.vertices, normals, vertex_colors])

        mix = self.shape_color_fraction
        colors = shape_colors*mix + vertex_colors*(1 - mix)

        self._finalize_primitive_arrays(
            positions, orientations, colors, images, normals, self.indices)
