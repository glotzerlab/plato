import numpy as np
from ... import draw
from ... import math

class Ellipsoids(draw.Ellipsoids):
    __doc__ = draw.Ellipsoids.__doc__

    def render(self, rotation=(1, 0, 0, 0), **kwargs):
        rotation = np.asarray(rotation)

        positions = math.quatrot(rotation[np.newaxis, :], self.positions)

        lines = []
        for (p, c, a) in zip(positions, self.colors[:, :3],
                                1 - self.colors[:, 3]):
            args = p.tolist() + [self.a, self.b, self.c] + c.tolist() + [a]
            lines.append('sphere {{<{},{},{}> 1 scale<{}, {}, {}> pigment {{color '
                         '<{},{},{}> transmit {}}}}}'.format(*args))
        return lines
