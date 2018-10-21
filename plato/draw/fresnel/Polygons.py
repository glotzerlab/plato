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
        angles = np.arctan2(self.orientations[:, 3], self.orientations[:, 0])*2
        heights = np.ones(len(self.positions))*0.5
        geometry = fresnel.geometry.Prism(
            scene=scene,
            vertices=self.vertices,
            position=self.positions,
            angle=angles,
            height=heights,
            color=self.colors[:, :3],
            material=self._material,
            outline_width=self.outline)
        return geometry
