import itertools

import numpy as np

from .internal import Shape, ShapeDecorator, ShapeAttribute

@ShapeDecorator
class Ellipsoids(Shape):
    """A collection of ellipsoids with identical dimensions.

    Each ellipsoid can have its own position, orientation, and
    color. All shapes drawn by this primitive share common principal
    axis lengths.
    """

    _ATTRIBUTES = list(itertools.starmap(ShapeAttribute, [
        ('positions', np.float32, (0, 0, 0), 2, True,
         'Position of each particle'),
        ('orientations', np.float32, (1, 0, 0, 0), 2, True,
         'Orientation quaternion of each particle'),
        ('colors', np.float32, (.5, .5, .5, 1), 2, True,
         'Color, RGBA, [0, 1] for each particle'),
        ('a', np.float32, .5, 0, False,
         'Radius in the x-direction'),
        ('b', np.float32, .5, 0, False,
         'Radius in the y-direction'),
        ('c', np.float32, .5, 0, False,
         'Radius in the z-direction'),
        ]))
