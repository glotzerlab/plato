import collections
import itertools

import numpy as np

from ... import draw, mesh
from ...draw import internal

LightInfo = collections.namedtuple(
    'LightInfo', ['normal', 'magnitude'])

@internal.ShapeDecorator
class Spheres(draw.Spheres):
    __doc__ = draw.Spheres.__doc__

    _ATTRIBUTES = draw.Spheres._ATTRIBUTES + list(itertools.starmap(
        internal.ShapeAttribute, [
            ('light_levels', np.uint32, 3, 0, False,
             'Number of quantized light levels to use'),
        ]))

    def render(self, rotation=(1, 0, 0, 0), name_suffix='', illo_id='illo',
               ambient_light=0.4, directional_light=[], **kwargs):
        # in the zdog coordinate system, x is to the right, y is down,
        # and z is toward you
        lines = []

        light_levels = np.linspace(0, 1, self.light_levels + 2)[1:-1]

        directional_light = np.atleast_2d(directional_light)

        light_info = []
        for light in directional_light:
            mag = np.linalg.norm(light)
            normal = light/mag

            light_info.append(LightInfo(normal, mag))

        particles = zip(*mesh.unfoldProperties([
            self.positions*(1, -1, 1), self.diameters, self.colors*255]))
        for i, (position, (diameter,), color) in enumerate(particles):
            group_index = 'sphere_{}_{}'.format(name_suffix, i)

            lines.append("""
            let {group_index} = new Zdog.Group({{
                addTo: {illo_id},
                translate: {{x: {pos[0]}, y: {pos[1]}, z: {pos[2]}}},
                updateSort: true,
            }});""".format(
                group_index=group_index, illo_id=illo_id, pos=position))

            (r, g, b) = map(int, ambient_light*color[:3])
            color_str = '"rgba({}, {}, {}, {})"'.format(r, g, b, color[3]/255)

            lines.append("""
            new Zdog.Shape({{
                addTo: {group_index},
                stroke: {diameter},
                color: {color},
            }});""".format(group_index=group_index, pos=position,
                           diameter=diameter, color=color_str))

            for (light, level_fraction) in itertools.product(
                    light_info, light_levels):
                offset = -0.5*diameter*(1 - level_fraction)*light.normal*(1, -1, 1)

                this_color = color.copy()
                light_level = 1 - level_fraction
                this_color[:3] *= ambient_light + light_level*light.magnitude
                this_color.clip(0, 255, this_color)

                (r, g, b) = map(int, this_color[:3])

                # RGB components are 0-255, A component is a float 0-1
                color_str = '"rgba({}, {}, {}, {})"'.format(r, g, b, color[3]/255)

                lines.append("""
                new Zdog.Shape({{
                    addTo: {group_index},
                    translate: {{x: {pos[0]}, y: {pos[1]}, z: {pos[2]}}},
                    color: {color},
                    stroke: {diameter},
                    fill: true,
                }});
                """.format(
                    group_index=group_index, pos=offset,
                    diameter=diameter*level_fraction, color=color_str))

        return lines
