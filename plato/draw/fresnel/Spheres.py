import fresnel

from ... import draw
from .FresnelPrimitive import FresnelPrimitive

class Spheres(FresnelPrimitive, draw.Spheres):
    __doc__ = draw.Spheres.__doc__

    def render(self, scene):
        geometry = fresnel.geometry.Sphere(
            scene=scene,
            position=self.positions,
            radius=self.radii,
            color=fresnel.color.linear(self.colors),
            material=self._material)
        return geometry
