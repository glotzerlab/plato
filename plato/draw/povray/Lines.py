import itertools

import numpy as np

from ... import draw
from ..internal import ShapeDecorator, ShapeAttribute
from ... import math as pmath

@ShapeDecorator
class Lines(draw.Lines):
    __doc__ = draw.Lines.__doc__

    _ATTRIBUTES = draw.Lines._ATTRIBUTES + list(itertools.starmap(ShapeAttribute, [
        ('cap_mode', np.int32, 0, 0, False,
         'Cap mode for lines (0: default, 1: round)'),
        ]))

    def render(self, rotation=(1, 0, 0, 0), translation=(0, 0, 0), **kwargs):
        rotation = np.asarray(rotation)

        lines = []

        start_points = pmath.quatrot(rotation[np.newaxis, :], self.start_points)
        start_points += translation
        end_points = pmath.quatrot(rotation[np.newaxis, :], self.end_points)
        end_points += translation

        for (start, end, width, color, a) in zip(start_points,
                                                 end_points,
                                                 self.widths/2,
                                                 self.colors[:, :3],
                                                 1 - self.colors[:, 3]):
            if self.cap_mode:
                args = start.tolist() + [width] + end.tolist() + [width] + \
                       color.tolist() + [a]
                lines.append('sphere_sweep {{linear_spline 2, <{},{},{}>, {}, '
                             '<{},{},{}>, {} pigment {{color <{},{},{}> transmit '
                             '{}}} }}'.format(*args))
            else:
                args = start.tolist() + end.tolist() + [width] + \
                       color.tolist() + [a]
                lines.append('cylinder {{<{},{},{}> <{},{},{}> {} pigment {{color '
                             '<{},{},{}> transmit {}}} }}'.format(*args))

        return lines
