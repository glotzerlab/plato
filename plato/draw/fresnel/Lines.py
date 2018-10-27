import fresnel
import itertools
import numpy as np
from ... import draw
from ..internal import ShapeAttribute

class Lines(draw.Lines):
    __doc__ = draw.Lines.__doc__

    _ATTRIBUTES = draw.Lines._ATTRIBUTES

    _ATTRIBUTES.extend(list(itertools.starmap(ShapeAttribute, [
        ('outline', np.float32, 0, 0, 'Outline width for all particles')
    ])))

    def __init__(self, *args, material=None, **kwargs):
        if material is None:
            self._material = fresnel.material.Material(primitive_color_mix=1)
            self._material.solid = 1
        else:
            self._material = material
        draw.Lines.__init__(self, *args, **kwargs)

    def render(self, scene):
        geometry = fresnel.geometry.Cylinder(
            scene=scene,
            N=len(self.start_points),
            material=self._material,
            outline_width=self.outline)
        geometry.points[:, 0, :] = self.start_points
        geometry.points[:, 1, :] = self.end_points
        geometry.radius[:] = self.widths/2
        geometry.color[:, 0, :] = self.colors[:, :3]
        geometry.color[:, 1, :] = self.colors[:, :3]
        return geometry
