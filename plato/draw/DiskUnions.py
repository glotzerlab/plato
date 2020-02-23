import itertools

import numpy as np

from .internal import Shape, ShapeDecorator, ShapeAttribute

@ShapeDecorator
class DiskUnions(Shape):
    """A collection of identical disk-union bodies in 2D.

    A `DiskUnions` object consists of one or more disks, each with its
    own radius and color. Each object has its own position and
    orientation that affect the final position of the constituent
    disks.
    """

    _ATTRIBUTES = list(itertools.starmap(ShapeAttribute, [
        ('positions', np.float32, (0, 0), 2, True,
         'Position of each particle'),
        ('orientations', np.float32, (1, 0, 0, 0), 2, True,
         'Orientation quaternion of each particle'),
        ('colors', np.float32, (.5, .5, .5, 1), 2, False,
         'Color, RGBA, [0, 1] for each disk in the union'),
        ('points', np.float32, (0, 0), 2, False,
         'Positions in local coordinates for the disks in the union, to be replicated for each particle'),
        ('radii', np.float32, .5, 1, False,
         'Radius of each disk in the union'),
        ('outline', np.float32, 0, 0, False,
         'Outline width for all particles')
        ]))

    @property
    def angles(self):
        """Orientation of each union, in radians"""
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

    @property
    def diameters(self):
        """Diameter of each disk in the union."""
        return 2*self._attributes.get('radii', .5)

    @diameters.setter
    def diameters(self, value):
        self.radii = 0.5*value
