import numpy as np

from ... import draw
from ... import mesh as pmesh
from ... import geometry
from ... import math as pmath

class ConvexSpheropolyhedra(draw.ConvexSpheropolyhedra):
    __doc__ = draw.ConvexSpheropolyhedra.__doc__

    def render(self, rotation=(1, 0, 0, 0), name_suffix='',
               translation=(0, 0, 0), **kwargs):
        rotation = np.asarray(rotation)
        (positions, orientations, colors) = pmesh.unfoldProperties([
            self.positions, self.orientations, self.colors])
        quat_magnitude = np.linalg.norm(orientations, axis=-1, keepdims=True)

        lines = []
        decomp = geometry.convexDecomposition(self.vertices)
        mesh = pmesh.convexSpheropolyhedronMesh(self.vertices, self.radius)
        meshStr = 'mesh2 {{vertex_vectors {{{} {}}} ' \
                  'face_indices {{{} {}}}}}'.format(
                      len(mesh.image), ' '.join('<{},{},{}>'.format(*v)
                                                for v in mesh.image),
                      len(mesh.indices), ' '.join('<{},{},{}>'.format(*v)
                                                  for v in mesh.indices))
        edges = ['cylinder {{<{0[0]},{0[1]},{0[2]}> <{1[0]},{1[1]},{1[2]}> '
                 '{2}}}'.format(
                     decomp.vertices[i], decomp.vertices[j],
                     np.asscalar(self.radius))
                 for (i, j) in decomp.edges]
        spheres = ['sphere {{<{0[0]},{0[1]},{0[2]}> {1}}}'.format(
            v, np.asscalar(self.radius)) for v in decomp.vertices]
        shapeName = 'spoly{}'.format(name_suffix)
        shapedef = '#declare {} = union {{\n{}\n}}'.format(
            shapeName, '\n'.join(elt for elt in [meshStr] + edges + spheres))
        lines.append(shapedef)

        qs = pmath.quatquat(rotation[np.newaxis, :], orientations/quat_magnitude)
        rotmat = np.array([[1 - 2*qs[:, 2]**2 - 2*qs[:, 3]**2,
                            2*(qs[:, 1]*qs[:, 2] - qs[:, 3]*qs[:, 0]),
                            2*(qs[:, 1]*qs[:, 3] + qs[:, 2]*qs[:, 0])],
                           [2*(qs[:, 1]*qs[:, 2] + qs[:, 3]*qs[:, 0]),
                            1 - 2*qs[:, 1]**2 - 2*qs[:, 3]**2,
                            2*(qs[:, 2]*qs[:, 3] - qs[:, 1]*qs[:, 0])],
                           [2*(qs[:, 1]*qs[:, 3] - qs[:, 2]*qs[:, 0]),
                            2*(qs[:, 1]*qs[:, 0] + qs[:, 2]*qs[:, 3]),
                            1 - 2*qs[:, 1]**2 - 2*qs[:, 2]**2]])
        rotmat = rotmat.transpose([2, 1, 0]).reshape((-1, 9))
        rotmat[:] *= quat_magnitude[:, 0, np.newaxis]**2

        positions = pmath.quatrot(rotation[np.newaxis, :], positions)
        positions += translation

        for (p, m, c) in zip(positions, rotmat, colors[:, :3]):
            args = [shapeName] + m.tolist() + p.tolist() + c.tolist()
            lines.append('object {{{} matrix <{},{},{},{},{},{},{},{},{},'
                         '{},{},{}> pigment {{color <{},{},{}>}}}}'.format(
                             *args))

        return lines
