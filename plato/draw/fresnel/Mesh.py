import itertools
import warnings

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
        # The fresnel backend does not support separate shape colors for
        # each replica. The closest approximation is to set the material
        # color and primitive color mix for all replicas.
        if not np.allclose(self.shape_colors, self.shape_colors[0]):
            warnings.warn(
                "Multiple shape colors were provided, but only the first "
                "provided shape color will be used for all mesh replicas "
                "in the primitive.")
        # Blend colors to match the specified shape color (only the first shape color is used)
        self._material.color = fresnel.color.linear(self.shape_colors[0])
        self._material.primitive_color_mix = 1-self.shape_color_fraction
        geometry = fresnel.geometry.Mesh(
            scene=scene,
            vertices=vertices,
            position=self.positions,
            orientation=self.orientations,
            color=color,
            material=self._material,
            outline_width=self.outline)
        return geometry
