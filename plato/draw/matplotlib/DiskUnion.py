import numpy as np
from ... import draw
from matplotlib.patches import Circle, Wedge, Polygon
from matplotlib.collections import PatchCollection
from matplotlib.transforms import Affine2D

class DiskUnion(draw.DiskUnion):
    __doc__ = draw.DiskUnion.__doc__

    def render(self, axes, aa_pixel_size=0, **kwargs):
        collections = []

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
            patches = PatchCollection(patches)
            outline_colors = np.zeros_like(self.colors)
            outline_colors[:, 3] = self.colors[:, 3]
            patches.set_facecolor(outline_colors)
            collections.append(patches)
        else:
            aa_pixel_size = 0

        shifted_radii = self.radii - outline + aa_pixel_size

        patches = []
        for (position, angle, scale) in zip(self.positions, self.angles, scale_factors):
            tf = Affine2D().scale(scale).rotate(angle).translate(*position)
            for i in range(len(self.points)):
                patches.append(Circle(points[i], radius=shifted_radii[i], transform=tf))

        patches = PatchCollection(patches)
        collections.append(patches)
        patches.set_facecolor(self.colors)

        for collection in collections:
            axes.add_collection(collection)
