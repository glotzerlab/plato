import fresnel
from ... import draw
from .FresnelPrimitive import FresnelPrimitiveSolid
import rowan

class Spheropolygons(FresnelPrimitiveSolid, draw.Spheropolygons):
    __doc__ = draw.Spheropolygons.__doc__

    def render(self, scene):
        geometry = fresnel.geometry.Polygon(
            scene=scene,
            vertices=self.vertices,
            position=self.positions,
            angle=rowan.geometry.angle(rowan.normalize(self.orientations)),
            color=fresnel.color.linear(self.colors),
            rounding_radius=self.radius,
            material=self._material,
            outline_width=self.outline)
        return geometry
