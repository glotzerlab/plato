import itertools

import numpy as np

from .internal import Shape, ShapeDecorator, ShapeAttribute

@ShapeDecorator
class SpherePoints(Shape):
    """A collection of points, useful for illustrating 3D density maps."""

    _ATTRIBUTES = list(itertools.starmap(ShapeAttribute, [
        ('points', np.float32, (1, 0, 0), 2, True,
         'Points to be rendered'),
        ('blur', np.float32, 3, 0, False,
         'Blurring factor dictating the size of each point'),
        ('intensity', np.float32, 1e3, 0, False,
         'Scaling factor dictating the magnitude of the color value of each point'),
        ('on_surface', np.uint32, 1, 0, False,
         'True if the points should always be projected onto the surface of a sphere')
        ]))
