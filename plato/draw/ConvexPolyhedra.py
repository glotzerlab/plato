import itertools
import numpy as np
from .internal import Shape, ShapeDecorator, ShapeAttribute

@ShapeDecorator
class ConvexPolyhedra(Shape):
    """A collection of identical convex polyhedra."""

    _ATTRIBUTES = list(itertools.starmap(ShapeAttribute, [
        ('positions', np.float32, (0, 0, 0), 2,
         'Position of each particle'),
        ('orientations', np.float32, (1, 0, 0, 0), 2,
         'Orientation quaternion of each particle'),
        ('colors', np.float32, (.5, .5, .5, 1), 2,
         'Color, RGBA, [0, 1] for each particle'),
        ('vertices', np.float32, (0, 0, 0), 2,
         'Vertices in local coordinates for the shape, to be replicated for each particle'),
        ]))
