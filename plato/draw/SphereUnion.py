import itertools
import numpy as np
from .internal import Shape, ShapeDecorator, ShapeAttribute

@ShapeDecorator
class SphereUnion(Shape):
    """A collection of identical sphere-union bodies in 3D.

    A "SphereUnion" object has a common union of points for the
    whole collection. Each sphere in the union can have it's own color
    and radius. Points in the union should be specified in counterclockwise order.
    """

    _ATTRIBUTES = list(itertools.starmap(ShapeAttribute, [
        ('positions', np.float32, (0, 0, 0), 2, True,
         'Position of each particle'),
        ('orientations', np.float32, (1, 0, 0, 0), 2, True,
         'Orientation quaternion of each particle'),
        ('colors', np.float32, (.5, .5, .5, 1), 2, False,
         'Color, RGBA, [0, 1] for each sphere in the union'),
        ('points', np.float32, (0, 0, 0), 2, False,
         'Positions in local coordinates for the spheres in the union, to be replicated for each particle (CCW order)'),
        ('radii', np.float32, .5, 1, True,
         'Radius of each sphere in the union')
        ]))

    @property
    def diameters(self):
        """Diameter of each particle."""
        return 2*self._attributes.get('radii', .5)

    @diameters.setter
    def diameters(self, value):
        self.radii = 0.5*np.atleast_1d(value)
