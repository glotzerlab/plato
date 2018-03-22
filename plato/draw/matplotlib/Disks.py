import numpy as np
from ... import draw
from matplotlib.patches import Circle, Wedge
from matplotlib.collections import PatchCollection

class Disks(draw.Disks):
    __doc__ = draw.Disks.__doc__

    def render(self, axes):
        collections = []
        outline = self.outline

        if outline > 0:
            patches = []
            for (position, radius) in zip(self.positions, self.radii):
                patches.append(Wedge(position, radius, 0, 360, width=outline))
            patches = PatchCollection(patches)
            outline_colors = np.zeros_like(self.colors)
            outline_colors[:, 3] = self.colors[:, 3]
            patches.set_facecolor(outline_colors)
            collections.append(patches)

        patches = []
        for (position, radius) in zip(self.positions, self.radii - outline):
            patches.append(Circle(position, radius))
        patches = PatchCollection(patches)
        patches.set_facecolor(self.colors)
        collections.append(patches)

        for collection in collections:
            axes.add_collection(collection)
