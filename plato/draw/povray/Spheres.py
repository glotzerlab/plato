import numpy as np

from ... import draw
from ... import math
from ... import mesh

class Spheres(draw.Spheres):
    __doc__ = draw.Spheres.__doc__

    def render(self, rotation=(1, 0, 0, 0), translation=(0, 0, 0), **kwargs):
        rotation = np.asarray(rotation)

        (positions, radii, colors) = mesh.unfoldProperties([
            self.positions, self.radii, self.colors])
        positions = math.quatrot(rotation[np.newaxis, :], positions)
        positions += translation

        lines = []
        for (p, r, c, a) in zip(positions, radii[:, 0], colors[:, :3],
                                1 - colors[:, 3]):
            args = p.tolist() + [r] + c.tolist() + [a]
            lines.append('sphere {{<{},{},{}> {} pigment {{color '
                         '<{},{},{}> transmit {}}}}}'.format(*args))
        return lines
