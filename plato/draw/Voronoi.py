import itertools

import numpy as np

from .internal import Shape, ShapeDecorator, ShapeAttribute

@ShapeDecorator
class Voronoi(Shape):
    """A Voronoi diagram of a set of 2D points.

    The region of space nearest to each given point will be colored by
    the color associated with that point.
    """

    _ATTRIBUTES = list(itertools.starmap(ShapeAttribute, [
        ('positions', np.float32, (0, 0), 2, True,
         'Position of each point'),
        ('colors', np.float32, (.5, .5, .5, 1), 2, True,
         'Color, RGBA, [0, 1] for each point')
        ]))
