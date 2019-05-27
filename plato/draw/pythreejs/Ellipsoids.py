from collections import defaultdict
import itertools
from ... import draw
from ... import mesh
from .internal import ThreeJSPrimitive
from ..internal import ShapeAttribute, ShapeDecorator
import numpy as np
import pythreejs

def fibonacciPositions(n_b, a=.5, b=0.5, c=0.5):
    m = np.arange(n_b).astype(np.float32)
    phi = m*np.pi*(3 - np.sqrt(5))
    vy = 2*m/n_b + 1/n_b - 1
    return np.array([a*np.sqrt(1 - vy**2)*np.cos(phi),
                     b*vy, c*np.sqrt(1 - vy**2)*np.sin(phi)]).T

@ShapeDecorator
class Ellipsoids(draw.Ellipsoids, ThreeJSPrimitive):
    __doc__ = draw.Ellipsoids.__doc__

    _ATTRIBUTES = draw.Ellipsoids._ATTRIBUTES + list(
        itertools.starmap(ShapeAttribute, [
        ('vertex_count', np.int32, 64, 0, False,
         'Number of vertices used to render ellipsoid')
    ]))

    def update_arrays(self):
        if not self._dirty_attributes:
            return

        vertices = fibonacciPositions(self.vertex_count, self.a, self.b, self.c)

        (vertices, indices) = mesh.convexHull(vertices)
        (positions, orientations, colors, images) = mesh.unfoldProperties(
            [self.positions, self.orientations, self.colors],
            [vertices])

        # these are incorrect normals, but this looks to be the most
        # straightforward way to have the normals get serialized
        normals = images.copy()

        self._finalize_primitive_arrays(
            positions, orientations, colors, images, normals, indices)
