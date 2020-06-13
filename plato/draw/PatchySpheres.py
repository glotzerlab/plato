import itertools

import numpy as np

from .internal import ShapeDecorator, ShapeAttribute
from .Spheres import Spheres

@ShapeDecorator
class PatchySpheres(Spheres):
    """A collection of patchy spheres in 3D.

    Each sphere can have a different position, orientation, base
    color, and diameter. Spheres also have a set of patches, specified
    by plane equations (a normal vector (x, y, z) and offset w) and
    associated colors (RGBA). Plane equations are specified for a
    diameter 2 sphere and each shape is scaled by its diameter.
    """

    _ATTRIBUTES = Spheres._ATTRIBUTES + list(itertools.starmap(ShapeAttribute, [
        ('orientations', np.float32, (1, 0, 0, 0), 2, True,
         'Orientation of each particle'),
        ('patch_planes', np.float32, (0, 0, 0, 0), 2, False,
         'Plane equations (x, y, z, w) for patches, specified for a sphere of diameter 2'),
        ('patch_colors', np.float32, (0.5, 0.5, 0.5, 1), 2, False,
         'Colors (RGBA) for each patch'),
        ('shape_color_fraction', np.float32, 0, 0, False,
         'Fraction of a patch\'s color that should be assigned based on colors'),
        ]))

    @property
    def patch_unit_angles(self):
        """Unit+angle specification for patch directions and sizes.

        Patches are specified in this way as an array of (x, y, z,
        theta) values, with x, y, and z specifying a unit vector and
        theta specifying the angle swept out by the patch.
        """
        result = self.patch_planes.copy()
        n, h = result[:, :3], result[:, 3]
        length = np.linalg.norm(n, axis=-1)
        result[:, :3] /= length[:, np.newaxis]
        result[:, 3] = 2*np.arccos(h/length)
        result[np.any(np.logical_not(np.isfinite(result)), axis=-1)] = (1, 0, 0, 0)
        return result

    @patch_unit_angles.setter
    def patch_unit_angles(self, value):
        value = np.atleast_2d(value).copy()
        length = np.linalg.norm(value[:, :3], -1, keepdims=True)
        value[:, :3] /= length
        value[:, 3] = np.cos(value[:, 3]*.5)
        value[np.any(np.logical_not(np.isfinite(value)), axis=-1)] = (1, 0, 0, 0)
        self.patch_planes = value
