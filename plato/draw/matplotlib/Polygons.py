import numpy as np
from ... import math
from ... import geometry
from ... import draw
from matplotlib.collections import PatchCollection
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Polygon
from matplotlib.transforms import Affine2D

class Polygons(draw.Polygons):
    __doc__ = draw.Polygons.__doc__

    def render(self, axes, aa_pixel_size=0, **kwargs):
        collections = []

        vertices = self.vertices
        scale_factors = np.linalg.norm(self.orientations, axis=-1)**2

        if self.outline > 0:
            tessellation = geometry.Polygon(self.vertices)
            outline = geometry.Outline(tessellation, self.outline)

            outer_vertices = vertices
            vertices = outline.inner.vertices

            commands = [Path.MOVETO] + (vertices.shape[0] - 1)*[Path.LINETO] + [Path.CLOSEPOLY]
            commands = 2*commands

            # reverse the inner vertices order to make an open
            # polygon. Duplicate the first vertex of each polygon to
            # close the shapes.
            outline_vertices = np.concatenate(
                [outer_vertices, outer_vertices[:1], vertices[::-1], vertices[:1]], axis=0)

            outline_path = Path(outline_vertices, commands)

            patches = []
            for (position, angle, scale) in zip(self.positions, self.angles, scale_factors):
                tf = Affine2D().scale(scale).rotate(angle).translate(*position)
                patches.append(PathPatch(outline_path.transformed(tf)))
            patches = PatchCollection(patches)

            outline_colors = np.zeros_like(self.colors)
            outline_colors[:, 3] = self.colors[:, 3]
            patches.set_facecolor(outline_colors)
            collections.append(patches)

            vertices += np.sign(vertices)*aa_pixel_size

        patches = []
        for (position, angle, scale) in zip(self.positions, self.angles, scale_factors):
            tf = Affine2D().scale(scale).rotate(angle).translate(*position)
            patches.append(Polygon(vertices, closed=True, transform=tf))
        patches = PatchCollection(patches)
        patches.set_facecolor(self.colors)
        collections.append(patches)

        for collection in collections:
            axes.add_collection(collection)
