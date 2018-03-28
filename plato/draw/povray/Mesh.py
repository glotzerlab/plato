import numpy as np
from ... import draw
from ... import mesh

class Mesh(draw.Mesh):
    __doc__ = draw.Mesh.__doc__

    def render(self, rotation=(1, 0, 0, 0), name_suffix='', **kwargs):
        lines = []

        verts = self.vertices
        vertex_vectors = ' '.join('<{},{},{}>'.format(*v) for v in verts)
        texture_list = ' '.join('texture{{pigment{{rgb <{},{},{}> '
                                'transmit {}}}}}'.format(
                                    *(list(v[:3])+[1 - v[3]]))
                                for v in self.colors)
        face_indices = ', '.join('<{},{},{}>,{},{},{}'.format(*(2*list(v)))
                                 for v in self.indices)
        meshStr = 'mesh2 {{vertex_vectors {{{} {}}} ' \
                  'texture_list {{{} {}}} face_indices {{{} {}}}}}'.format(
                      len(verts), vertex_vectors,
                      len(verts), texture_list,
                      len(self.indices), face_indices)
        shapeName = 'mesh_shape{}'.format(name_suffix)
        shapedef = '#declare {} = {}'.format(shapeName, meshStr)
        lines.append(shapedef)

        q = rotation.copy()
        rotmat = np.array([[1 - 2*q[2]**2 - 2*q[3]**2,
                            2*(q[1]*q[2] - q[3]*q[0]),
                            2*(q[1]*q[3] + q[2]*q[0])],
                           [2*(q[1]*q[2] + q[3]*q[0]),
                            1 - 2*q[1]**2 - 2*q[3]**2,
                            2*(q[2]*q[3] - q[1]*q[0])],
                           [2*(q[1]*q[3] - q[2]*q[0]),
                            2*(q[1]*q[0] + q[2]*q[3]),
                            1 - 2*q[1]**2 - 2*q[2]**2]])
        rotmat = rotmat.transpose().reshape((9,))

        args = [shapeName] + rotmat.tolist() + [0, 0, 0]
        lines.append('object {{{} matrix <{},{},{},{},{},{},{},{},{},'
                     '{},{},{}>}}'.format(*args))

        return lines
