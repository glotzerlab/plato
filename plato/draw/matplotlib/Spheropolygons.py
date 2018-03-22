import numpy as np
from ... import math
from ... import geometry
from ... import draw
from matplotlib.collections import PatchCollection
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.transforms import Affine2D

class Spheropolygons(draw.Spheropolygons):
    __doc__ = draw.Spheropolygons.__doc__

    def render(self, axes, aa_pixel_size=0, **kwargs):
        collections = []

        vertices = self.vertices
        # distance vector from each vertex to the next vertex in a given shape
        delta_verts = np.roll(vertices, -1, axis=0) - vertices
        delta_verts /= np.linalg.norm(delta_verts, axis=-1, keepdims=True)
        # the normal vector of the edge originating at each vertex
        vert_normals = np.transpose([delta_verts[:, 1], -delta_verts[:, 0]])

        # start and end angles for the arc around each vertex, in degrees
        degree_ends = 180/np.pi*np.arctan2(vert_normals[..., 1], vert_normals[..., 0])
        degree_starts = np.roll(degree_ends, 1, axis=0)

        radius = self.radius
        outline = self.outline
        delta_outline = radius - outline

        if outline > 0:
            # sketch out the outline, using the full radius
            commands = [Path.MOVETO]
            positions = [vertices[-1] + vert_normals[-1]*radius]
            for (vert, norm, degrees_start, degrees_end) in zip(
                    vertices, np.roll(vert_normals, 1, axis=0),
                    degree_starts, degree_ends):
                commands.append(Path.LINETO)
                positions.append(vert + norm*radius)
                arc = Path.arc(degrees_start, degrees_end)
                for (pos, cmd) in arc.iter_segments():
                    if cmd in {Path.STOP, Path.MOVETO}:
                        continue
                    pos = pos.reshape((-1, 2))
                    commands.extend(pos.shape[0]*[cmd])
                    positions.extend(vert[np.newaxis] + pos*radius)

            # repeat the outline path creation but in reverse to make
            # the hole for the colored portion of the shape
            commands.append(Path.MOVETO)
            positions.append(vertices[0] + vert_normals[-1]*delta_outline)
            for (vert, norm, degrees_end, degrees_start) in zip(
                    vertices[::-1], vert_normals[::-1],
                    degree_ends[::-1], degree_starts[::-1]):
                commands.append(Path.LINETO)
                positions.append(vert + norm*delta_outline)
                arc = Path.arc(degrees_start, degrees_end)
                for (pos, cmd) in reversed(list(arc.iter_segments())):
                    if cmd in {Path.STOP, Path.MOVETO}:
                        continue
                    pos = pos.reshape((-1, 2))[::-1]
                    commands.extend(pos.shape[0]*[cmd])
                    positions.extend(vert[np.newaxis] + pos*delta_outline)
            path = Path(positions, commands)

            patches = []
            for (position, angle) in zip(self.positions, self.angles):
                tf = Affine2D().rotate(angle).translate(*position)
                patches.append(PathPatch(path.transformed(tf)))
            patches = PatchCollection(patches)
            outline_colors = np.zeros_like(self.colors)
            outline_colors[:, 3] = self.colors[:, 3]
            patches.set_facecolor(outline_colors)
            collections.append(patches)

            vertices += np.sign(vertices)*aa_pixel_size

        # create the path for the filled/colored portion of the shape
        commands = [Path.MOVETO]
        positions = [vertices[-1] + vert_normals[-1]*delta_outline]
        for (vert, norm, degrees_start, degrees_end) in zip(
                vertices, np.roll(vert_normals, 1, axis=0), degree_starts, degree_ends):
            commands.append(Path.LINETO)
            positions.append(vert + norm*delta_outline)
            arc = Path.arc(degrees_start, degrees_end)
            for (pos, cmd) in arc.iter_segments():
                if cmd in {Path.STOP, Path.MOVETO}:
                    continue
                pos = pos.reshape((-1, 2))*delta_outline
                commands.extend(pos.shape[0]*[cmd])
                positions.extend(vert[np.newaxis] + pos)
        path = Path(positions, commands)

        patches = []
        for (position, angle) in zip(self.positions, self.angles):
            tf = Affine2D().rotate(angle).translate(*position)
            patches.append(PathPatch(path.transformed(tf)))
        patches = PatchCollection(patches)
        patches.set_facecolor(self.colors)
        collections.append(patches)

        for collection in collections:
            axes.add_collection(collection)
