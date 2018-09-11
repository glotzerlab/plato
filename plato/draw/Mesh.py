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
    """

    _ATTRIBUTES = list(itertools.starmap(ShapeAttribute, [
        ('vertices', np.float32, (0, 0, 0), 2,
         'Vertex array specifying coordinates of the mesh nodes'),
        ('indices', np.uint32, (0, 0, 0), 2,
         'Indices of the vertex array specifying individual triangles'),
        ('colors', np.float32, (.5, .5, .5, 1), 2,
         'Color, RGBA, [0, 1] for each vertex')
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
