import fresnel
import numpy as np
from ... import draw

class Disks(draw.Disks):
    __doc__ = draw.Disks.__doc__

    def __init__(self, *args, material=None, **kwargs):
        if material is None:
            self._material = fresnel.material.Material(primitive_color_mix=1)
            self._material.solid = 1
        else:
            self._material = material
        draw.Disks.__init__(self, *args, **kwargs)

    def render(self, scene):
        geometry = fresnel.geometry.Sphere(
            scene=scene,
            N=len(self.positions),
            material=self._material,
            outline_width=self.outline)
        geometry.position[:, :2] = self.positions
        geometry.position[:, 2] = 0
        geometry.radius[:] = self.radii
        geometry.color[:] = self.colors[:, :3]
        return geometry
