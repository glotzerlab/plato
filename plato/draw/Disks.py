import itertools

import numpy as np

from .internal import Shape, ShapeDecorator, ShapeAttribute

@ShapeDecorator
class Disks(Shape):
    """A collection of disks in 2D.

    Each disk can have a different color and diameter.
    """

    _ATTRIBUTES = list(itertools.starmap(ShapeAttribute, [
        ('positions', np.float32, (0, 0), 2, True,
         'Position of each particle'),
        ('colors', np.float32, (.5, .5, .5, 1), 2, True,
         'Color, RGBA, [0, 1] for each particle'),
        ('radii', np.float32, .5, 1, True,
         'Radius of each particle'),
        ('outline', np.float32, 0, 0, False,
         'Outline width for all particles')
        ]))

    @property
    def diameters(self):
        """Diameter of each particle."""
        return 2*self._attributes.get('radii', .5)

    @diameters.setter
    def diameters(self, value):
        self.radii = 0.5*value
