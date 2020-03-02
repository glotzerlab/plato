import numpy as np

from ... import draw, geometry, mesh
from .internal import PolygonRenderer

class Spheropolygons(draw.Spheropolygons, PolygonRenderer):
    __doc__ = draw.Spheropolygons.__doc__

    def _get_path(self):
        corner_vertices = geometry.insetPolygon(self.vertices, -self.radius)
        mesh_object = mesh.spheropolygonMesh(self.vertices, self.radius, 1)

        result = []
        corner_vertices = (corner_vertices*(1, -1))[::-1].tolist()
        arc_pieces = zip(mesh_object.image*(1, -1), mesh_object.vertex_types)
        for (vertex, vertex_type) in arc_pieces:
            if vertex_type == 0 or vertex_type == 2:
                corner = corner_vertices.pop()

            if vertex_type == 2:
                result.append((
                    "{{arc: [{{x: {corner[0]}, y: {corner[1]}}},"
                    "        {{x: {end[0]}, y: {end[1]}}}]}}""").format(
                        corner=corner, end=vertex))
            elif vertex_type == 0 or vertex_type == 10:
                result.append(
                    "{{x: {pos[0]}, y: {pos[1]}}}".format(pos=vertex))

        return ', '.join(result)

    def render(self, *args, **kwargs):
        if self.outline:
            kwargs['outline'] = self.outline
        kwargs['stroke'] = False
        return PolygonRenderer.render(self, *args, **kwargs)
