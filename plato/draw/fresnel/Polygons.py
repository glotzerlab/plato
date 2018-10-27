import fresnel
import numpy as np
from ... import draw

class Polygons(draw.Polygons):
    __doc__ = draw.Polygons.__doc__

    def __init__(self, *args, material=None, **kwargs):
        if material is None:
            self._material = fresnel.material.Material(primitive_color_mix=1)
            self._material.solid = 1
        else:
            self._material = material
        draw.Polygons.__init__(self, *args, **kwargs)

    def render(self, scene):
        bottom = np.zeros((len(self.vertices), 3))
        bottom[:, :2] = self.vertices
        top = bottom.copy()
        top[:, 2] = 0.5
        vertices = np.concatenate((bottom, top))
        polyhedron_info = fresnel.util.convex_polyhedron_from_vertices(vertices)
        geometry = fresnel.geometry.ConvexPolyhedron(
            scene=scene,
            polyhedron_info=polyhedron_info,
            N=len(self.positions),
            material=self._material,
            outline_width=self.outline)
        geometry.position[:, :2] = self.positions
        geometry.position[:, 2] = 0
        geometry.orientation[:] = self.orientations
        geometry.color[:] = self.colors[:, :3]
        return geometry
