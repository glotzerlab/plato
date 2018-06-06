from collections import defaultdict
from ... import draw
from ... import mesh
from .internal import ThreeJSPrimitive
import numpy as np
import pythreejs

def fibonacciPositions(n_b, R=.5):
    m = np.arange(n_b).astype(np.float32)
    phi = m*np.pi*(3 - np.sqrt(5))
    vy = 2*m/n_b + 1/n_b - 1
    return R*np.array([np.sqrt(1 - vy**2)*np.cos(phi),
                       vy, np.sqrt(1 - vy**2)*np.sin(phi)]).T

class Spheres(draw.Spheres, ThreeJSPrimitive):
    __doc__ = draw.Spheres.__doc__

    def update_arrays(self):
        if not self._dirty_attributes:
            return

        # TODO make this a configurable attribute
        vertices = fibonacciPositions(64)

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
