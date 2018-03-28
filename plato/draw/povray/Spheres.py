import numpy as np
from ... import draw
from ... import math

class Spheres(draw.Spheres):
    __doc__ = draw.Spheres.__doc__

    def render(self, rotation=(1, 0, 0, 0), **kwargs):
        rotation = np.asarray(rotation)

        positions = math.quatrot(rotation[np.newaxis, :], self.positions)

        lines = []
        for (p, r, c, a) in zip(positions, self.radii, self.colors[:, :3],
                                1 - self.colors[:, 3]):
            args = p.tolist() + [r] + c.tolist() + [a]
            lines.append('sphere {{<{},{},{}> {} pigment {{color '
                         '<{},{},{}> transmit {}}}}}'.format(*args))
        return lines
