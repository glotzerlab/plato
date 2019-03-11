import fresnel
from ... import draw
from ... import math
from .FresnelPrimitive import FresnelPrimitive
import numpy as np

class SphereUnions(draw.SphereUnions, FresnelPrimitive):
    __doc__ = draw.SphereUnions.__doc__

    def __init__(self, *args, material=None, **kwargs):
        FresnelPrimitive.__init__(self, *args, material, **kwargs)
        draw.SphereUnions.__init__(self, *args, **kwargs)

    def render(self, scene):

        positions = np.tile(self.positions[:, np.newaxis, :], (1, len(self.points), 1))
        positions += math.quatrot(self.orientations[:, np.newaxis], self.points[np.newaxis])

        radii = np.repeat(self.radii[np.newaxis, :], len(self.positions),axis=0)
        colors = np.repeat(self.colors[np.newaxis, :], len(self.positions), axis=0)

        geometry = fresnel.geometry.Sphere(
            scene=scene,
            position=positions.reshape((-1, 3)),
            radius=radii.flatten(),
            color=fresnel.color.linear(colors.reshape(-1,4)),
            material=self._material)
        return geometry
