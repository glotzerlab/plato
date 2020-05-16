import itertools

import numpy as np

from ... import draw
from ... import mesh as pmesh
from ... import geometry
from ... import math as pmath
from ..internal import ShapeAttribute, ShapeDecorator

@ShapeDecorator
class ConvexPolyhedra(draw.ConvexPolyhedra):
    __doc__ = draw.ConvexPolyhedra.__doc__

    _ATTRIBUTES = draw.ConvexPolyhedra._ATTRIBUTES + list(
        itertools.starmap(ShapeAttribute, [
        ('outline', np.float32, 0, 0, False,
         'Outline width for all particles')
    ]))

    def render(self, rotation=(1, 0, 0, 0), name_suffix='',
               translation=(0, 0, 0), **kwargs):
        rotation = np.asarray(rotation)
        (shape_positions, orientations, colors) = pmesh.unfoldProperties([
            self.positions, self.orientations, self.colors])
        quat_magnitude = np.linalg.norm(orientations, axis=-1, keepdims=True)

        lines = []

        if self.outline:
            diameter = np.sqrt(np.max(np.sum(self.vertices**2, axis=-1)))
            outline = self.outline*diameter
            decomp = geometry.convexDecomposition(self.vertices)
            edges = ['cylinder {{<{0[0]},{0[1]},{0[2]}> '
                     '<{1[0]},{1[1]},{1[2]}> {2}}}'.format(
                         decomp.vertices[i], decomp.vertices[j],
                         np.asscalar(outline/2))
                     for (i, j) in decomp.edges]
            spheres = ['sphere {{<{0[0]},{0[1]},{0[2]}> {1}}}'.format(
                v, np.asscalar(outline/2)) for v in decomp.vertices]
            shapeName = 'spoly{}'.format(name_suffix)
            shapedef = '#declare {} = union {{\n{}\n}}'.format(
                shapeName, '\n'.join(elt for elt in edges + spheres))
            lines.append(shapedef)

            qs = pmath.quatquat(rotation[np.newaxis, :],
                                orientations/quat_magnitude)
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

            positions = pmath.quatrot(rotation[np.newaxis, :], shape_positions)
            positions += translation

            for (p, m, a) in zip(positions, rotmat, 1 - colors[:, 3]):
                args = [shapeName] + m.tolist() + p.tolist() + [0, 0, 0, a]
                lines.append('object {{{} matrix <{},{},{},{},{},{},{},{},{},'
                             '{},{},{}> pigment {{color <{},{},{}> transmit {} }}}}'.format(
                                 *args))

        mesh = pmesh.convexPolyhedronMesh(self.vertices)
        meshStr = 'mesh2 {{vertex_vectors {{{} {}}} ' \
                  'face_indices {{{} {}}}}}'.format(
            len(mesh.image), ' '.join('<{},{},{}>'.format(*v)
                                      for v in mesh.image),
            len(mesh.indices), ' '.join('<{},{},{}>'.format(*v)
                                        for v in mesh.indices))
        shapeName = 'poly{}'.format(name_suffix)
        shapedef = '#declare {} = {}'.format(shapeName, meshStr)
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
        rotmat *= quat_magnitude[:, 0, np.newaxis]**2

        positions = pmath.quatrot(rotation[np.newaxis, :], shape_positions)
        positions += translation

        for (p, m, (r, g, b), a) in zip(positions, rotmat, colors[:, :3],
                                        1 - colors[:, 3]):
            args = [shapeName] + m.tolist() + p.tolist() + [r, g, b, a]
            lines.append('object {{{} matrix <{},{},{},{},{},{},{},{},{},'
                         '{},{},{}> pigment {{color <{},{},{}> transmit '
                         '{}}}}}'.format(*args))

        return lines
