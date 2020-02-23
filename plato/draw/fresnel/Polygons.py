import fresnel
import rowan

from ... import draw
from .FresnelPrimitive import FresnelPrimitiveSolid

class Polygons(FresnelPrimitiveSolid, draw.Polygons):
    __doc__ = draw.Polygons.__doc__

    def render(self, scene):
        geometry = fresnel.geometry.Polygon(
            scene=scene,
            vertices=self.vertices,
            position=self.positions,
            angle=rowan.geometry.angle(rowan.normalize(self.orientations)),
            color=fresnel.color.linear(self.colors),
            material=self._material,
            outline_width=self.outline)
        return geometry
