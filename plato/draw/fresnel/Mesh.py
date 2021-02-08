import itertools

import fresnel
import numpy as np

from ... import draw
from ..internal import ShapeAttribute, ShapeDecorator
from .FresnelPrimitive import FresnelPrimitive

@ShapeDecorator
class Mesh(FresnelPrimitive, draw.Mesh):
    __doc__ = draw.Mesh.__doc__

    _ATTRIBUTES = draw.Mesh._ATTRIBUTES + list(
        itertools.starmap(ShapeAttribute, [
        ('outline', np.float32, 0, 0, False,
         'Outline width for all particles')
    ]))

    def render(self, scene):
        # Convert from vertices shape (num_unique_vertices, 3) and indices with
        # shape (num_triangles, 3) to (3 * num_triangles, 3) array
        vertices = self.vertices[self.indices].reshape(-1, 3)
        color = fresnel.color.linear(self.colors)[self.indices].reshape(-1, 3)
        self._material.primitive_color_mix = self.shape_color_fraction
        geometry = fresnel.geometry.Mesh(
            scene=scene,
            vertices=vertices,
            position=self.positions,
            orientation=self.orientations,
            color=color,
            material=self._material,
            outline_width=self.outline)
        return geometry
