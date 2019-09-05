import numpy as np
from ... import geometry
from ... import draw
from .internal import PatchUser
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Polygon
from matplotlib.transforms import Affine2D

class Polygons(draw.Polygons, PatchUser):
    __doc__ = draw.Polygons.__doc__

    def _render_patches(self, axes, aa_pixel_size=0, **kwargs):
        result = []

        vertices = self.vertices
        scale_factors = np.linalg.norm(self.orientations, axis=-1)**2

        if self.outline > 0:
            outer_vertices = vertices
            vertices = geometry.insetPolygon(vertices, self.outline)

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

            outline_colors = np.zeros_like(self.colors)
            outline_colors[:, 3] = self.colors[:, 3]
            result.append((patches, outline_colors))

            vertices += np.sign(vertices)*aa_pixel_size

        patches = []
        for (position, angle, scale) in zip(self.positions, self.angles, scale_factors):
            tf = Affine2D().scale(scale).rotate(angle).translate(*position)
            patches.append(Polygon(vertices, closed=True, transform=tf))
        result.append((patches, self.colors))

        return result
