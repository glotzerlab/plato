import collections
import itertools

import numpy as np

from ... import draw, mesh
from ...draw import internal

LightInfo = collections.namedtuple(
    'LightInfo', ['normal', 'magnitude'])

@internal.ShapeDecorator
class Disks(draw.Disks):
    __doc__ = draw.Disks.__doc__

    def render(self, rotation=(1, 0, 0, 0), name_suffix='', illo_id='illo',
               **kwargs):
        # in the zdog coordinate system, x is to the right, y is down,
        # and z is toward you
        lines = []

        particles = zip(*mesh.unfoldProperties([
            self.positions*(1, -1), self.diameters, self.colors*255]))
        for i, (position, (diameter,), color) in enumerate(particles):
            group_index = 'disk_{}_{}'.format(name_suffix, i)

            (r, g, b) = map(int, color[:3])
            color_str = '"rgba({}, {}, {}, {})"'.format(
                r, g, b, color[3]/255)

            lines.append("""
            new Zdog.Shape({{
                addTo: {illo_id},
                translate: {{x: {pos[0]}, y: {pos[1]}}},
                stroke: {diameter},
                color: {color},
            }});""".format(
                group_index=group_index, illo_id=illo_id, pos=position,
                diameter=diameter, color=color_str))

        return lines
