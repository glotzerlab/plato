import itertools

import numpy as np

from .internal import Shape, ShapeDecorator, ShapeAttribute

@ShapeDecorator
class ConvexPolyhedra(Shape):
    """A collection of identically-shaped convex polyhedra.

    Each shape can have its own position, orientation, and color.
    """

    _ATTRIBUTES = list(itertools.starmap(ShapeAttribute, [
        ('positions', np.float32, (0, 0, 0), 2, True,
         'Position of each particle'),
        ('orientations', np.float32, (1, 0, 0, 0), 2, True,
         'Orientation quaternion of each particle'),
        ('colors', np.float32, (.5, .5, .5, 1), 2, True,
         'Color, RGBA, [0, 1] for each particle'),
        ('vertices', np.float32, (0, 0, 0), 2, False,
         'Vertices in local coordinates for the shape, to be replicated for each particle'),
        ('outline', np.float32, 0, 0, False,
         'Outline width for all shapes'),
        ]))
