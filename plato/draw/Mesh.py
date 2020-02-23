import itertools

import numpy as np

from .internal import Shape, ShapeDecorator, ShapeAttribute
from .. import mesh

@ShapeDecorator
class Mesh(Shape):
    """A 3D triangle mesh.

    Meshes are specified by an array of vertices and indices
    identifying triangles within that vertex array. Colors are
    assigned per-vertex and interpolated between vertices.

    Meshes with a common set of vertices and face indices can be
    replicated multiple times using a set of positions and
    orientations. In order to set the color of individual replicas of
    the Mesh object, use the `shape_colors` and `shape_color_fraction`
    attributes.
    """

    _ATTRIBUTES = list(itertools.starmap(ShapeAttribute, [
        ('vertices', np.float32, (0, 0, 0), 2, False,
         'Vertex array specifying coordinates of the mesh nodes'),
        ('indices', np.uint32, (0, 0, 0), 2, False,
         'Indices of the vertex array specifying individual triangles (Nx3)'),
        ('colors', np.float32, (.5, .5, .5, 1), 2, False,
         'Color, RGBA, [0, 1] for each vertex'),
        ('positions', np.float32, (0, 0, 0), 2, True,
         'Central positions for each mesh to be replicated'),
        ('orientations', np.float32, (1, 0, 0, 0), 2, True,
         'Orientations for each mesh to be replicated'),
        ('shape_colors', np.float32, (.5, .5, .5, 1), 2, True,
         'Color, RGBA, [0, 1] for each replica (shape) of the mesh'),
        ('shape_color_fraction', np.float32, 0, 0, False,
         'Fraction of a vertex\'s color that should be assigned based on shape_colors')
        ]))

    @classmethod
    def double_sided(cls, vertices, indices, colors, thickness=1e-3, **kwargs):
        """Create a double-sided Mesh object.

        Typically the "inside" of a Mesh (as determined by the order
        of triangle indices) is unlit. This method replicates the
        vertices, one for each side, after computing the appropriate
        normals.
        """
        vertices = np.asarray(vertices, dtype=np.float32)
        indices = np.asarray(indices, dtype=np.uint32)
        normal = mesh.computeNormals_(vertices, indices)

        new_vertices = np.concatenate([
            vertices + thickness/2*normal,
            vertices - thickness/2*normal], axis=0)
        new_indices = np.concatenate([
            indices,
            indices[:, ::-1] + len(vertices)], axis=0)
        new_colors = np.concatenate([colors, colors], axis=0)

        return cls(vertices=new_vertices, indices=new_indices,
                   colors=new_colors, **kwargs)
