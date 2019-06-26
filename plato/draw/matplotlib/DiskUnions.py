import numpy as np
from ... import draw
from .internal import PatchUser
from matplotlib.patches import Circle, Wedge
from matplotlib.transforms import Affine2D

class DiskUnions(draw.DiskUnions, PatchUser):
    __doc__ = draw.DiskUnions.__doc__

    def _render_patches(self, axes, aa_pixel_size=0, **kwargs):
        result = []

        outline = self.outline
        points = self.points
        colors = self.colors
        radii = self.radii

        scale_factors = np.linalg.norm(self.orientations, axis=-1)**2

        if outline > 0:
            patches = []
            for (position, angle, scale) in zip(self.positions, self.angles, scale_factors):
                tf = Affine2D().scale(scale).rotate(angle).translate(*position)
                for i in range(len(self.points)):
                    patches.append(Wedge(points[i], radii[i], 0, 360, width=outline, transform=tf))
            outline_colors = np.zeros_like(self.colors)
            outline_colors[:, 3] = self.colors[:, 3]
            outline_colors = np.tile(outline_colors, (len(self.positions), 1))

            # in case the user gave inconsistent numbers of positions/angles/colors
            N = min(len(patches), len(outline_colors))
            result.append((patches[:N], outline_colors[:N]))
        else:
            aa_pixel_size = 0

        shifted_radii = self.radii - outline + aa_pixel_size

        patches = []
        for (position, angle, scale) in zip(self.positions, self.angles, scale_factors):
            tf = Affine2D().scale(scale).rotate(angle).translate(*position)
            for i in range(len(self.points)):
                patches.append(Circle(points[i], radius=shifted_radii[i], transform=tf))
        colors = np.tile(self.colors, (len(self.positions), 1))
        N = min(len(patches), len(colors))
        result.append((patches[:N], colors[:N]))

        return result
