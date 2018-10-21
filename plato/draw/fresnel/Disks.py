import fresnel
import numpy as np
from ... import draw

class Disks(draw.Disks):
    __doc__ = draw.Disks.__doc__

    def __init__(self, *args, material=None, **kwargs):
        if material is None:
            self.material = fresnel.material.Material(primitive_color_mix=1)
        else:
            self.material = material
        draw.Disks.__init__(self, *args, **kwargs)

    def render(self, scene):
        positions = np.zeros((len(self.positions), 3))
        positions[:, :2] = self.positions
        geometry = fresnel.geometry.Sphere(
            scene=scene,
            position=positions,
            radius=self.radii,
            color=self.colors[:, :3],
            material=self.material,
            outline_width=self.outline)
        return geometry
