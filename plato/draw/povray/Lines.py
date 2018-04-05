import numpy as np
from ... import draw
from ... import math as pmath

class Lines(draw.Lines):
    __doc__ = draw.Lines.__doc__

    def render(self, rotation=(1, 0, 0, 0), **kwargs):
        rotation = np.asarray(rotation)

        lines = []

        start_points = pmath.quatrot(rotation[np.newaxis, :], self.start_points)
        end_points = pmath.quatrot(rotation[np.newaxis, :], self.end_points)

        for (start, end, width, color, a) in zip(start_points,
                                                 end_points,
                                                 self.widths/2,
                                                 self.colors[:, :3],
                                                 1 - self.colors[:, 3]):
            args = start.tolist() + end.tolist() + [width] + \
                   color.tolist() + [a]
            lines.append('cylinder {{<{},{},{}> <{},{},{}> {} pigment {{color '
                         '<{},{},{}> transmit {}}} }}'.format(*args))

        return lines
