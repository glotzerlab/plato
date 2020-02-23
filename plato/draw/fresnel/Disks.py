import fresnel

from ... import draw
from .FresnelPrimitive import FresnelPrimitiveSolid

class Disks(FresnelPrimitiveSolid, draw.Disks):
    __doc__ = draw.Disks.__doc__

    def render(self, scene):
        geometry = fresnel.geometry.Sphere(
            scene=scene,
            N=len(self.positions),
            material=self._material,
            outline_width=self.outline)
        geometry.position[:, :2] = self.positions
        geometry.position[:, 2] = 0
        geometry.radius[:] = self.radii
        geometry.color[:] = fresnel.color.linear(self.colors)
        return geometry
