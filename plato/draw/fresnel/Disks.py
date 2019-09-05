import fresnel
from ... import draw
from .FresnelPrimitive import FresnelPrimitive

class Disks(draw.Disks, FresnelPrimitive):
    __doc__ = draw.Disks.__doc__

    def __init__(self, *args, material=None, **kwargs):
        FresnelPrimitive.__init__(self, *args, material, **kwargs)
        if material is None:
            self._material.solid = 1
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
        geometry.color[:] = fresnel.color.linear(self.colors)
        return geometry
