import itertools
import numpy as np
from ..internal import ShapeDecorator, ShapeAttribute
from ... import draw
from matplotlib.collections import PathCollection
from matplotlib.path import Path

@ShapeDecorator
class Voronoi(draw.Voronoi):
    __doc__ = draw.Voronoi.__doc__

    _ATTRIBUTES = draw.Voronoi._ATTRIBUTES + list(
        itertools.starmap(ShapeAttribute, [
        ('outline', np.float32, 0, 0, False,
         'Outline width between Voronoi cells, in scene units'),
    ]))

    def render(self, axes, aa_pixel_size=0, **kwargs):
        import scipy as sp, scipy.spatial

        collections = []
        paths = []

        vor = sp.spatial.Voronoi(self.positions)

        centers = self.positions

        for (point_index, reg_index) in enumerate(vor.point_region):
            reg = vor.regions[reg_index]
            if reg_index == -1 or -1 in reg:
                # always add a path so we can set_facecolor() later
                # without removing colors corresponding to empty paths
                commands = [Path.MOVETO]
                vertices = [centers[point_index]]
            else:
                vertices = vor.vertices[reg]
                commands = [Path.MOVETO] + (vertices.shape[0] - 1)*[Path.LINETO] + [Path.CLOSEPOLY]
                vertices = np.concatenate([vertices, vertices[:1]], axis=0)

                vertices += np.sign(vertices - centers[point_index])*0.5*aa_pixel_size

            paths.append(Path(vertices, commands))

        collection = PathCollection(paths)
        collection.set_facecolor(self.colors)
        collections.append(collection)

        if self.outline:
            paths = []

            for ridge_indices in vor.ridge_vertices:
                if -1 in ridge_indices or len(ridge_indices) != 2:
                    continue

                i, j = ridge_indices
                ri = vor.vertices[i]
                rij = vor.vertices[j] - ri
                norm = rij/np.linalg.norm(rij, axis=-1, keepdims=True)
                perp = 0.5*np.array([-norm[1], norm[0]])

                vertices = [
                    ri + perp*self.outline,
                    ri + rij + perp*self.outline,
                    ri + rij - perp*self.outline,
                    ri - perp*self.outline,
                    ri + perp*self.outline,
                ]

                commands = [Path.MOVETO] + 3*[Path.LINETO] + [Path.CLOSEPOLY]

                paths.append(Path(vertices, commands))

            outline_colors = np.zeros((len(paths), 3))

            collection = PathCollection(paths)
            collection.set_facecolor(outline_colors)
            collections.append(collection)

        for collection in collections:
            axes.add_collection(collection)
