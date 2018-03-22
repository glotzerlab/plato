import numpy as np
from ... import math
from ... import geometry
from ... import draw
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Polygon
from matplotlib.collections import PatchCollection

class Polygons(draw.Polygons):
    __doc__ = draw.Polygons.__doc__

    def render(self, axes):
        collections = []

        positions_3d = np.pad(
            self.positions, [(0, 0), (0, 1)], mode='constant', constant_values=0)
        verts_3d = np.pad(
            self.vertices, [(0, 0), (0, 1)], mode='constant', constant_values=0)

        # Np, Nv, 3
        verts = math.quatrot(self.orientations[:, np.newaxis, :], verts_3d[np.newaxis, :, :])
        verts += positions_3d[:, np.newaxis, :]
        verts = verts[..., :2]

        if self.outline > 0:
            tessellation = geometry.Polygon(self.vertices)
            outline = geometry.Outline(tessellation, self.outline)

            outer_verts = verts
            # Np, Nv, 3
            verts_3d = np.pad(
                outline.inner.vertices, [(0, 0), (0, 1)], mode='constant', constant_values=0)
            verts = math.quatrot(self.orientations[:, np.newaxis, :], verts_3d[np.newaxis, :, :])
            verts += positions_3d[:, np.newaxis, :]
            verts = verts[..., :2]

            commands = [Path.MOVETO] + (verts.shape[1] - 1)*[Path.LINETO] + [Path.CLOSEPOLY]
            commands = 2*commands

            # reverse the inner vertices order to make an open
            # polygon. Duplicate the first vertex of each polygon to
            # close the shapes.
            outline_vertices = np.concatenate(
                [outer_verts, outer_verts[:, :1], verts[:, ::-1], verts[:, :1]], axis=1)

            patches = []
            for positions in outline_vertices:
                path = Path(positions, commands)
                patches.append(PathPatch(path))
            patches = PatchCollection(patches)
            outline_colors = np.zeros_like(self.colors)
            outline_colors[:, 3] = self.colors[:, 3]
            patches.set_facecolor(outline_colors)
            collections.append(patches)

        patches = []
        for vertices in verts:
            patches.append(Polygon(vertices, closed=True))
        patches = PatchCollection(patches)
        patches.set_facecolor(self.colors)
        collections.append(patches)

        for collection in collections:
            axes.add_collection(collection)
