import numpy as np

from ... import draw
from ... import math
from ... import mesh

class SphereUnions(draw.SphereUnions):
    __doc__ = draw.SphereUnions.__doc__

    def render(self, rotation=(1, 0, 0, 0), translation=(0, 0, 0), **kwargs):
        rotation = np.asarray(rotation)

        (positions, orientations) = mesh.unfoldProperties([
            self.positions, self.orientations])

        positions = np.tile(positions[:, np.newaxis, :], (1, len(self.points), 1))
        positions += math.quatrot(orientations[:, np.newaxis], self.points[np.newaxis])
        positions += translation

        radii = np.repeat(self.radii[np.newaxis, :], len(positions),axis=0)
        colors = np.repeat(self.colors[np.newaxis, :], len(positions), axis=0)

        colors_reshaped = colors.reshape(-1,4)

        lines = []
        for (p, r, c, a) in zip(positions.reshape((-1, 3)), radii.flatten(), colors_reshaped[:, :3],
                                1 - colors_reshaped[:, 3]):
            args = p.tolist() + [r] + c.tolist() + [a]
            lines.append('sphere {{<{},{},{}> {} pigment {{color '
                         '<{},{},{}> transmit {}}}}}'.format(*args))
        return lines
