from matplotlib.patches import Circle, Wedge
import numpy as np

from ... import draw
from ... import mesh
from .internal import PatchUser

class Disks(draw.Disks, PatchUser):
    __doc__ = draw.Disks.__doc__

    def _render_patches(self, axes, aa_pixel_size=0, **kwargs):
        result = []
        outline = self.outline

        (positions, radii, colors) = mesh.unfoldProperties([
            self.positions, self.radii, self.colors])

        if outline > 0:
            patches = []
            for (position, (radius,)) in zip(positions, radii):
                patches.append(Wedge(position, radius, 0, 360, width=outline))
            outline_colors = np.zeros_like(colors)
            outline_colors[:, 3] = colors[:, 3]
            result.append((patches, outline_colors))
        else:
            aa_pixel_size = 0

        shifted_radii = radii[:, 0] - outline + aa_pixel_size

        patches = []
        for (position, radius) in zip(positions, shifted_radii):
            patches.append(Circle(position, radius))
        result.append((patches, colors))

        return result
