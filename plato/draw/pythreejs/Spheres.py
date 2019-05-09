from collections import defaultdict
import itertools
from ... import draw
from ... import mesh
from .internal import ThreeJSPrimitive
from ..internal import ShapeAttribute, ShapeDecorator
import numpy as np
import pythreejs

def fibonacciPositions(n_b, R=.5):
    m = np.arange(n_b).astype(np.float32)
    phi = m*np.pi*(3 - np.sqrt(5))
    vy = 2*m/n_b + 1/n_b - 1
    return R*np.array([np.sqrt(1 - vy**2)*np.cos(phi),
                       vy, np.sqrt(1 - vy**2)*np.sin(phi)]).T

@ShapeDecorator
class Spheres(draw.Spheres, ThreeJSPrimitive):
    __doc__ = draw.Spheres.__doc__

    _ATTRIBUTES = draw.Spheres._ATTRIBUTES + list(
        itertools.starmap(ShapeAttribute, [
        ('vertex_count', np.int32, 64, 0, False,
         'Number of vertices used to render sphere')
    ]))

    def update_arrays(self):
        if not self._dirty_attributes:
            return

        vertices = fibonacciPositions(self.vertex_count)

        (vertices, indices) = mesh.convexHull(vertices)
        (positions, colors, diameters, images) = mesh.unfoldProperties(
            [self.positions, self.colors, self.diameters],
            [vertices])

        images *= diameters

        # these are incorrect normals, but this looks to be the most
        # straightforward way to have the normals get serialized
        normals = images.copy()

        self._finalize_primitive_arrays(
            positions, None, colors, images, normals, indices)
