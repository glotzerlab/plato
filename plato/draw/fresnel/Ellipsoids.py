import fresnel
import itertools
import numpy as np
from ... import draw
from ..internal import ShapeAttribute, ShapeDecorator
from .FresnelPrimitive import FresnelPrimitive

def fibonacciPositions(n_b, a=.5, b=0.5, c=0.5):
    m = np.arange(n_b).astype(np.float32)
    phi = m*np.pi*(3 - np.sqrt(5))
    vy = 2*m/n_b + 1/n_b - 1
    return np.array([a*np.sqrt(1 - vy**2)*np.cos(phi),
                     b*vy, c*np.sqrt(1 - vy**2)*np.sin(phi)]).T


@ShapeDecorator
class Ellipsoids(draw.Ellipsoids, FresnelPrimitive):
    __doc__ = draw.Ellipsoids.__doc__

    _ATTRIBUTES = draw.Ellipsoids._ATTRIBUTES + list(
        itertools.starmap(ShapeAttribute, [
        ('outline', np.float32, 0, 0, False,
         'Outline width for all particles'),
        ('vertex_count', np.int32, 256, 0, False,
         'Number of vertices used to render ellipsoid')
    ]))

    def __init__(self, *args, material=None, **kwargs):
        FresnelPrimitive.__init__(self, *args, material, **kwargs)
        draw.Ellipsoids.__init__(self, *args, **kwargs)

    def render(self, scene):
        vertices = fibonacciPositions(self.vertex_count, self.a, self.b, self.c)
        polyhedron_info = fresnel.util.convex_polyhedron_from_vertices(vertices)
        geometry = fresnel.geometry.ConvexPolyhedron(
            scene=scene,
            polyhedron_info=polyhedron_info,
            position=self.positions,
            orientation=self.orientations,
            color=fresnel.color.linear(self.colors),
            material=self._material,
            outline_width=self.outline)
        return geometry
