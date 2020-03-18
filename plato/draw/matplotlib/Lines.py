from matplotlib.path import Path
from matplotlib.patches import PathPatch
import numpy as np

from ... import math
from ... import mesh
from ... import draw
from .internal import PatchUser

class Lines(draw.Lines, PatchUser):
    __doc__ = draw.Lines.__doc__

    def _render_patches(self, axes, aa_pixel_size=0, rotation=(1, 0, 0, 0),
               ambient_light=0, directional_light=(-.1, -.25, -1), **kwargs):
        rotation = np.asarray(rotation)

        start_points, end_points, widths, colors = mesh.unfoldProperties([
            self.start_points, self.end_points, self.widths, self.colors])

        # rotate into scene orientation
        start_points = math.quatrot(rotation[np.newaxis], start_points)
        end_points = math.quatrot(rotation[np.newaxis], end_points)
        midpoints = 0.5*(start_points + end_points)
        zs = midpoints[:, 2]

        # calculate the vector perpendicular to each line segment
        deltas = end_points[:, :2] - start_points[:, :2]
        perps = np.array([-deltas[:, 1], deltas[:, 0]]).T
        perps /= np.linalg.norm(perps, axis=-1, keepdims=True)
        perps *= 0.5*widths
        perps[np.any(np.logical_not(np.isfinite(perps)), axis=-1)] = (1, 0)

        # angle of the vector perpendicular to each line segment
        angles = np.arctan2(perps[:, 1], perps[:, 0]) + np.pi
        angles[np.logical_not(np.isfinite(angles))] = 0
        angles_degrees = angles*180/np.pi

        # construct rectangles with offset vertices
        rectangles = [start_points[:, :2] - perps, end_points[:, :2] - perps,
                      end_points[:, :2] + perps, start_points[:, :2] + perps]

        if aa_pixel_size:
            for elt in rectangles:
                elt -= midpoints[:, :2]
                elt += np.sign(elt)*aa_pixel_size
                elt += midpoints[:, :2]

        patches = []
        for (z, angle, width, start, end, a, b, c, d) in zip(
                zs, angles_degrees, widths[:, 0], start_points[:, :2],
                end_points[:, :2], *rectangles):
            arc = Path.arc(angle, angle + 180)
            commands = [Path.MOVETO, Path.LINETO]
            vertices = [a, b]

            for (pos, cmd) in arc.iter_segments():
                cmd = cmd if cmd != Path.MOVETO else Path.LINETO
                if cmd == Path.STOP:
                    continue
                pos = pos.reshape((-1, 2))*width*0.5
                commands.extend(pos.shape[0]*[cmd])
                vertices.extend(end[np.newaxis] + pos)

            commands.append(Path.LINETO)
            vertices.append(c)

            commands.append(Path.LINETO)
            vertices.append(d)
            for (pos, cmd) in arc.iter_segments():
                cmd = cmd if cmd != Path.MOVETO else Path.LINETO
                if cmd == Path.STOP:
                    continue
                pos = pos.reshape((-1, 2))*width*0.5
                commands.extend(pos.shape[0]*[cmd])
                vertices.extend(start[np.newaxis] - pos)

            commands.append(Path.CLOSEPOLY)
            vertices.append(a)

            path = Path(vertices, commands)
            patches.append(PathPatch(path, zorder=z))

        return [(patches, colors)]
