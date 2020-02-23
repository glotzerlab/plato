from matplotlib.patches import Circle, Wedge
import numpy as np

from ... import draw
from .internal import PatchUser

class Disks(draw.Disks, PatchUser):
    __doc__ = draw.Disks.__doc__

    def _render_patches(self, axes, aa_pixel_size=0, **kwargs):
        result = []
        outline = self.outline

        if outline > 0:
            patches = []
            for (position, radius) in zip(self.positions, self.radii):
                patches.append(Wedge(position, radius, 0, 360, width=outline))
            outline_colors = np.zeros_like(self.colors)
            outline_colors[:, 3] = self.colors[:, 3]
            result.append((patches, outline_colors))
        else:
            aa_pixel_size = 0

        shifted_radii = self.radii - outline + aa_pixel_size

        patches = []
        for (position, radius) in zip(self.positions, shifted_radii):
            patches.append(Circle(position, radius))
        result.append((patches, self.colors))

        return result
