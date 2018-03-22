import itertools
import numpy as np
from .internal import Shape, ShapeDecorator, ShapeAttribute

@ShapeDecorator
class Spheres(Shape):
    """A collection of spheres. Each sphere can have a different color and
    diameter."""

    _ATTRIBUTES = list(itertools.starmap(ShapeAttribute, [
        ('positions', np.float32, (0, 0, 0), 2,
         'Position of each particle'),
        ('colors', np.float32, (.5, .5, .5, 1), 2,
         'Color, RGBA, [0, 1] for each particle'),
        ('radii', np.float32, .5, 1,
         'Radius of each particle'),
        ]))

    @property
    def diameters(self):
        return 2*self._attributes.get('radii', .5)

    @diameters.setter
    def diameters(self, value):
        self.radii = 0.5*value
