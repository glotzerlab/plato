import itertools
import numpy as np
from .internal import Shape, ShapeDecorator, ShapeAttribute

@ShapeDecorator
class Polygons(Shape):
    """A collection of 2D polygons with a common shape. Each polygon can
    have a different color."""

    _ATTRIBUTES = list(itertools.starmap(ShapeAttribute, [
        ('positions', np.float32, (0, 0), 2,
         'Position of each particle'),
        ('orientations', np.float32, (1, 0, 0, 0), 2,
         'Orientation quaternion of each particle'),
        ('colors', np.float32, (.5, .5, .5, 1), 2,
         'Color, RGBA, [0, 1] for each particle'),
        ('vertices', np.float32, (0, 0), 2,
         'Vertices in local coordinates for the shape, to be replicated for each particle'),
        ('outline', np.float32, 0, 0,
         'Outline width for all particles')
        ]))

    @property
    def angles(self):
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
