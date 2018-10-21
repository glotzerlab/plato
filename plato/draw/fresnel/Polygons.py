import fresnel
import numpy as np
from ... import draw

class Polygons(draw.Polygons):
    __doc__ = draw.Polygons.__doc__

    def __init__(self, *args, material=None, **kwargs):
        if material is None:
            self._material = fresnel.material.Material(primitive_color_mix=1)
        else:
            self._material = material
        draw.Polygons.__init__(self, *args, **kwargs)

    def render(self, scene):
        positions = np.zeros((len(self.positions), 3))
        positions[:, :2] = self.positions
        bottom = np.zeros((len(self.vertices), 3))
        bottom[:, :2] = self.vertices
        top = bottom.copy()
        top[:, 2] = 1
        vertices = np.concatenate((bottom, top))
        polyhedron_info = fresnel.util.convex_polyhedron_from_vertices(vertices)
        geometry = fresnel.geometry.ConvexPolyhedron(
            scene=scene,
            polyhedron_info=polyhedron_info,
            position=positions,
            orientation=self.orientations,
            color=self.colors[:, :3],
            material=self._material,
            outline_width=self.outline)
        return geometry
