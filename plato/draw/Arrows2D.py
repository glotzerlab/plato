import numpy as np

from .internal import ShapeDecorator
from .Polygons import Polygons

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
        super().__init__(*args, **kwargs)

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
        return np.linalg.norm(self.orientations, axis=-1)**2

    @magnitudes.setter
    def magnitudes(self, value):
        magnitudes = np.atleast_1d(value)
        quats = self.orientations

        N = max(quats.shape[0], magnitudes.shape[0])
        if magnitudes.shape[0] < N:
            magnitudes = np.concatenate(
                [magnitudes, np.ones(N - magnitudes.shape[0])])
        if quats.shape[0] < N:
            quats = np.concatenate(
                [quats, np.tile([[1, 0, 0, 0]], (N - quats.shape[0], 1))],
                axis=0)
        magnitudes /= np.linalg.norm(quats, axis=-1)**2
        self.orientations = quats*np.sqrt(magnitudes)[:, np.newaxis]
