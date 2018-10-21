import fresnel
from ... import draw

class Spheres(draw.Spheres):
    __doc__ = draw.Spheres.__doc__

    def __init__(self, *args, material=None, **kwargs):
        if material is None:
            self._material = fresnel.material.Material(primitive_color_mix=1)
        else:
            self._material = material
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
