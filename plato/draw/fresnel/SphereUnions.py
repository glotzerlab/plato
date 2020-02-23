import fresnel
import numpy as np

from ... import draw
from ... import math
from .FresnelPrimitive import FresnelPrimitive

class SphereUnions(FresnelPrimitive, draw.SphereUnions):
    __doc__ = draw.SphereUnions.__doc__

    def render(self, scene):
        positions = np.tile(self.positions[:, np.newaxis, :], (1, len(self.points), 1))
        positions += math.quatrot(self.orientations[:, np.newaxis], self.points[np.newaxis])

        radii = np.repeat(self.radii[np.newaxis, :], len(self.positions), axis=0)
        colors = np.repeat(self.colors[np.newaxis, :], len(self.positions), axis=0)

        geometry = fresnel.geometry.Sphere(
            scene=scene,
            position=positions.reshape((-1, 3)),
            radius=radii.flatten(),
            color=fresnel.color.linear(colors.reshape(-1, 4)),
            material=self._material)
        return geometry
