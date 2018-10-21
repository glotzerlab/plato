import fresnel
from ... import draw

class Disks(draw.Disks):
    __doc__ = draw.Disks.__doc__

    def __init__(self, material=None):
        if material is None:
            self.material = fresnel.material.Material(primitive_color_mix=1)
        else:
            self.material = material
        draw.Disks.__init__(self, *args, **kwargs)

    def render(self, scene):
        geometry = fresnel.geometry.Sphere(
            scene=scene,
            position=self.positions,
            radius=self.radii,
            color=self.colors[:, :3],
            material=self.material,
            outline_width=self.outline)
        return geometry
