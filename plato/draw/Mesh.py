import itertools
import numpy as np
from .internal import Shape, ShapeDecorator, ShapeAttribute

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
