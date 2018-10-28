import fresnel
from ... import draw
from . import FresnelPrimitive

class Spheres(draw.Spheres, FresnelPrimitive):
    __doc__ = draw.Spheres.__doc__

    def __init__(self, *args, material=None, **kwargs):
        FresnelPrimitive.__init__(self, *args, material, **kwargs)
        draw.Spheres.__init__(self, *args, **kwargs)

    def render(self, scene):
        geometry = fresnel.geometry.Sphere(
            scene=scene,
            position=self.positions,
            radius=self.radii,
            color=self.colors[:, :3],
            material=self._material,
            outline_width=self.outline)
        return geometry
