from matplotlib.patches import Circle, Wedge
from matplotlib.transforms import Affine2D
import numpy as np

from ... import draw
from ... import mesh
from .internal import PatchUser

class DiskUnions(draw.DiskUnions, PatchUser):
    __doc__ = draw.DiskUnions.__doc__

    def _render_patches(self, axes, aa_pixel_size=0, **kwargs):
        result = []

        outline = self.outline
        (points, colors, radii) = mesh.unfoldProperties([
            self.points, self.colors, self.radii])
        (positions, angles, orientations) = mesh.unfoldProperties([
            self.positions, self.angles, self.orientations])

        scale_factors = np.linalg.norm(orientations, axis=-1)**2

        if outline > 0:
            patches = []
            for (position, (angle,), scale) in zip(positions, angles, scale_factors):
                tf = Affine2D().scale(scale).rotate(angle).translate(*position)
                for (point, (radius,)) in zip(points, radii):
                    patches.append(Wedge(point, radius, 0, 360, width=outline, transform=tf))
            outline_colors = np.zeros_like(colors)
            outline_colors[:, 3] = colors[:, 3]
            outline_colors = np.tile(outline_colors, (len(positions), 1))

            result.append((patches, outline_colors))
        else:
            aa_pixel_size = 0

        shifted_radii = radii - outline + aa_pixel_size

        patches = []
        for (position, (angle,), scale) in zip(positions, angles, scale_factors):
            tf = Affine2D().scale(scale).rotate(angle).translate(*position)
            for (point, (radius,)) in zip(points, shifted_radii):
                patches.append(Circle(point, radius=radius, transform=tf))
        colors = np.tile(colors, (len(positions), 1))
        result.append((patches, colors))

        return result
