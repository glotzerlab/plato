import fresnel
import itertools
import numpy as np
from ... import draw
from ..internal import ShapeAttribute
from .FresnelPrimitive import FresnelPrimitive

class ConvexPolyhedra(draw.ConvexPolyhedra, FresnelPrimitive):
    __doc__ = draw.ConvexPolyhedra.__doc__

    _ATTRIBUTES = draw.ConvexPolyhedra._ATTRIBUTES

    _ATTRIBUTES.extend(list(itertools.starmap(ShapeAttribute, [
        ('outline', np.float32, 0, 0, 'Outline width for all particles')
    ])))

    def __init__(self, *args, material=None, **kwargs):
        FresnelPrimitive.__init__(self, *args, material, **kwargs)
        draw.ConvexPolyhedra.__init__(self, *args, **kwargs)

    def render(self, scene):
        polyhedron_info = fresnel.util.convex_polyhedron_from_vertices(self.vertices)
        geometry = fresnel.geometry.ConvexPolyhedron(
            scene=scene,
            polyhedron_info=polyhedron_info,
            position=self.positions,
            orientation=self.orientations,
            color=self.colors[:, :3],
            material=self._material,
            outline_width=self.outline)
        return geometry
