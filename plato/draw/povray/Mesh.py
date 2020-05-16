import numpy as np

from ... import draw
from ... import math as pmath
from ... import mesh

class Mesh(draw.Mesh):
    __doc__ = draw.Mesh.__doc__

    def render(self, rotation=(1, 0, 0, 0), name_suffix='',
               translation=(0, 0, 0), **kwargs):
        lines = []

        verts = self.vertices
        vertex_colors = self.colors
        if len(vertex_colors) < len(verts):
            vertex_colors = np.tile(
                vertex_colors, (int(np.ceil(len(verts)/len(vertex_colors))), 1))

        (positions, orientations, shape_colors) = mesh.unfoldProperties([
            self.positions, self.orientations, self.shape_colors])
        if len(shape_colors) < len(positions):
            shape_colors = np.tile(
                shape_colors, (int(np.ceil(len(positions)/len(shape_colors))), 1))

        blended_colors = (self.shape_color_fraction*shape_colors[:, np.newaxis, :] +
                          (1 - self.shape_color_fraction)*vertex_colors[np.newaxis, :, :])

        vertex_vectors = ' '.join('<{},{},{}>'.format(*v) for v in verts)
        face_indices = ', '.join('<{},{},{}>,{},{},{}'.format(*(2*list(v)))
                                 for v in self.indices)

        vertex_normals = mesh.computeNormals_(verts, self.indices)
        vertex_normal_text = ' '.join('<{},{},{}>'.format(*v) for v in vertex_normals)

        quat_magnitude = np.linalg.norm(orientations, axis=-1, keepdims=True)
        qs = pmath.quatquat(rotation[np.newaxis, :], orientations/quat_magnitude)
        rotmats = np.array([[1 - 2*qs[:, 2]**2 - 2*qs[:, 3]**2,
                            2*(qs[:, 1]*qs[:, 2] - qs[:, 3]*qs[:, 0]),
                            2*(qs[:, 1]*qs[:, 3] + qs[:, 2]*qs[:, 0])],
                           [2*(qs[:, 1]*qs[:, 2] + qs[:, 3]*qs[:, 0]),
                            1 - 2*qs[:, 1]**2 - 2*qs[:, 3]**2,
                            2*(qs[:, 2]*qs[:, 3] - qs[:, 1]*qs[:, 0])],
                           [2*(qs[:, 1]*qs[:, 3] - qs[:, 2]*qs[:, 0]),
                            2*(qs[:, 1]*qs[:, 0] + qs[:, 2]*qs[:, 3]),
                            1 - 2*qs[:, 1]**2 - 2*qs[:, 2]**2]])
        rotmats = rotmats.transpose([2, 1, 0]).reshape((-1, 9))
        rotmats *= quat_magnitude[:, 0, np.newaxis]**2

        positions = pmath.quatrot(rotation[np.newaxis, :], positions)
        positions += translation

        for (pos, rotmat, color) in zip(positions, rotmats, blended_colors):

            texture_list = ' '.join('texture{{pigment{{rgb <{},{},{}> '
                                    'transmit {}}}}}'.format(
                                        *(list(v[:3])+[1 - v[3]]))
                                    for v in color)
            print(len(verts), len(color))
            meshStr = 'mesh2 {{vertex_vectors {{{} {}}} ' \
                      'normal_vectors {{{}, {}}} ' \
                      'texture_list {{{} {}}} ' \
                      'face_indices {{{} {}}} ' \
                      'matrix <{},{},{},{},{},{},{},{},{},' \
                      '{},{},{}>}}'.format(
                          len(verts), vertex_vectors,
                          len(verts), vertex_normal_text,
                          len(verts), texture_list,
                          len(self.indices), face_indices,
                          *(rotmat.tolist() + pos.tolist())
                      )
            lines.append(meshStr)

        return lines
