import itertools

import numpy as np

from .internal import Shape, ShapeDecorator, ShapeAttribute

@ShapeDecorator
class Lines(Shape):
    """A collection of line segments.

    Each segment can have a different color and width. `Lines` can be
    used in both 2D and 3D scenes, but they are currently not shaded
    and may look out of place in 3D.
    """

    _ATTRIBUTES = list(itertools.starmap(ShapeAttribute, [
        ('start_points', np.float32, (0, 0, 0), 2, True,
         'Beginning coordinate for each line segment'),
        ('end_points', np.float32, (0, 0, 0), 2, True,
         'Ending coordinate for each line segment'),
        ('widths', np.float32, .1, 1, True,
         'Width of each line segment'),
        ('colors', np.float32, (.5, .5, .5, 1), 2, True,
         'Color, RGBA, [0, 1] for each line segment'),
        ]))
