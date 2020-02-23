import numpy as np
import rowan

from ... import draw
from ... import geometry
from .internal import ThreeJSPrimitive

class Lines(draw.Lines, ThreeJSPrimitive):
    __doc__ = draw.Lines.__doc__

    def update_arrays(self):
        if not self._dirty_attributes:
            return

        # TODO make number of facets a configurable attribute
        thetas = np.linspace(0, 2*np.pi, 10, endpoint=False)

        # to begin, pretend we are constructing a unit circle in the
        # xy plane; multiply xy by each line radius and z by each line
        # length before rotating and translating appropriately
        image = np.array([np.cos(thetas), np.sin(thetas), np.zeros_like(thetas)]).T
        image = np.concatenate([image, image + (0, 0, 1)], axis=0)

        # indices to make all triangles for a given Line object
        image_indices = np.tile(np.arange(2*len(thetas))[:, np.newaxis], (1, 3))
        image_indices[:len(thetas), 1] += 1
        image_indices[:len(thetas), 2] += len(thetas)
        image_indices[len(thetas):, 1] += 1 - len(thetas)
        image_indices[len(thetas):, 2] += 1
        image_indices[len(thetas) - 1, 1] -= len(thetas)
        image_indices[-1, 1:] -= len(thetas)

        cap_indices = np.array(list(
            geometry.fanTriangleIndices(np.arange(len(thetas))[np.newaxis])))
        image_indices = np.concatenate([
            image_indices,
            cap_indices[:, ::-1],
            len(thetas) + cap_indices
        ], axis=0)

        # normal vectors for each Line segment
        normals = self.end_points - self.start_points
        lengths = np.linalg.norm(normals, axis=-1, keepdims=True)
        normals /= lengths

        # find quaternion to rotate (0, 0, 1) into the direction each
        # Line is pointing
        quats = rowan.vector_vector_rotation(
            np.array([0, 0, 1.])[np.newaxis, :], normals)

        # Nlines*Nvertices*3
        vertices = np.tile(image[np.newaxis], (len(quats), 1, 1))
        # set xy according to line width
        vertices[:, :, :2] *= self.widths[:, np.newaxis, np.newaxis]*0.5
        # set z according to line length
        vertices[:, :, 2] *= lengths[:, np.newaxis, 0]
        # rotate appropriately
        vertices = rowan.rotate(quats[:, np.newaxis], vertices)
        # translation by start_points will happen in _finalize_primitive_arrays

        # these are incorrect normals, but this looks to be the most
        # straightforward way to have the normals get serialized
        normals = vertices - self.start_points[:, np.newaxis]

        colors = np.tile(self.colors[:, np.newaxis], (1, len(image), 1))

        positions = np.tile(self.start_points[:, np.newaxis], (1, len(image), 1))

        self._finalize_primitive_arrays(
            positions, None, colors, vertices, normals, image_indices)
