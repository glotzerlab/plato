from ... import draw
from ... import mesh

class Lines(draw.Lines):
    __doc__ = draw.Lines.__doc__

    def render(self, rotation=(1, 0, 0, 0), name_suffix='', illo_id='illo',
               ambient_light=0.4, directional_light=[], **kwargs):
        # in the zdog coordinate system, x is to the right, y is down,
        # and z is toward you
        lines = []

        particles = zip(*mesh.unfoldProperties([
            self.start_points*(1, -1, 1), self.end_points*(1, -1, 1),
            self.widths, self.colors*255]))
        for i, (start, end, (width,), color) in enumerate(particles):
            path = ', '.join('{{x: {}, y: {}, z: {}}}'.format(*v) for v in [start, end])

            (r, g, b) = map(int, color[:3])

            # RGB components are 0-255, A component is a float 0-1
            color_str = '"rgba({}, {}, {}, {})"'.format(r, g, b, color[3]/255)

            lines.append("""
            new Zdog.Shape({{
                addTo: {illo_id},
                color: {color},
                path: [{path}],
                stroke: {width},
                closed: false,
            }});
            """.format(
                illo_id=illo_id, color=color_str, path=path, width=width))

        return lines
