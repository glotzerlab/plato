import itertools

import numpy as np

from .internal import Shape, ShapeDecorator, ShapeAttribute

@ShapeDecorator
class Polygons(Shape):
    """A collection of polygons.

    A `Polygons` object has a common shape for the whole
    collection. Each shape can have a different orientation and
    color. Vertices should be specified in counterclockwise order.
    """

    _ATTRIBUTES = list(itertools.starmap(ShapeAttribute, [
        ('positions', np.float32, (0, 0), 2, True,
         'Position of each particle'),
        ('orientations', np.float32, (1, 0, 0, 0), 2, True,
         'Orientation quaternion of each particle'),
        ('colors', np.float32, (.5, .5, .5, 1), 2, True,
         'Color, RGBA, [0, 1] for each particle'),
        ('vertices', np.float32, (0, 0), 2, False,
         'Vertices in local coordinates for the shape, to be replicated for each particle (CCW order)'),
        ('outline', np.float32, 0, 0, False,
         'Outline width for all particles')
        ]))

    @property
    def angles(self):
        """Orientation of each particle, in radians"""
        quats = self.orientations
        return 2*np.arctan2(quats[:, 3], quats[:, 0])

    @angles.setter
    def angles(self, value):
        halfthetas = 0.5*np.atleast_2d(value).reshape((-1, 1))
        real = np.cos(halfthetas)
        imag = np.sin(halfthetas)
        zeros = np.zeros_like(real)
        quats = np.hstack([real, zeros, zeros, imag]).astype(np.float32)
        self.orientations = quats
