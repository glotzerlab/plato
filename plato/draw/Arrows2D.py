import itertools
import numpy as np
from .Polygons import Polygons
from .internal import attribute_setter, ShapeDecorator, ShapeAttribute

@ShapeDecorator
class Arrows2D(Polygons):
    """A collection of 2D arrows.

    Each arrow has an independent position, orientation, color, and
    magnitude. The shape of arrows can be configured by changing its
    `vertices` attribute. The default orientation and scale of the
    vertices is an arrow centered at (0, 0), pointing in the (1, 0)
    direction, with length 1.

    The origin of the arrows can be shifted to have the base lie on
    the given position by modifying `vertices`::

        arrows.vertices = arrows.vertices + (0.5, 0)
    """

    def __init__(self, *args, **kwargs):
        super(Polygons, self).__init__(*args, **kwargs)

        thickness = 0.14        # width of arrow shaft
        head_length = 0.35      # length from base of the head to the tip of the arrow
        head_width = 0.45       # wingspan from tip to tip of the arrow head
        head_edge_excess = 0.03 # how far back to pull the wingtips of the head past the base of the head
        vertices = [(0.5, 0.),
                    (0.5 - head_length, head_width/2.),
                    (0.5 - head_length + head_edge_excess, thickness/2.),
                    (-0.5, thickness/2.),
                    (-0.5, -thickness/2.),
                    (0.5 - head_length + head_edge_excess, -thickness/2.),
                    (0.5 - head_length, -head_width/2.)]
        if 'vertices' not in kwargs:
            self.vertices = vertices

    @property
    def magnitudes(self):
        """Magnitude (size scale) of each particle"""
        return np.linalg.norm(self.orientations, axis=-1)

    @magnitudes.setter
    def magnitudes(self, value):
        magnitudes = np.atleast_1d(value)
        attribute_setter(self, value, 'magnitudes', np.float32, 1, np.array(1))
        quats = self.orientations
        N = min(quats.shape[0], magnitudes.shape[0])
        quats[:N] *= (np.sqrt(magnitudes[:N])/np.linalg.norm(quats[:N], axis=-1))[:, np.newaxis]
        Polygons.orientations.fset(self, quats)

    @property
    def orientations(self):
        """Magnitude (size scale) of each particle"""
        return Polygons.orientations.fget(self)

    @orientations.setter
    def orientations(self, value):
        quats = np.atleast_2d(value)
        magnitudes = self.magnitudes
        N = min(quats.shape[0], magnitudes.shape[0])
        quats[:N] *= (np.sqrt(magnitudes[:N])/np.linalg.norm(quats[:N], axis=-1))[:, np.newaxis]
        Polygons.orientations.fset(self, quats)

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
