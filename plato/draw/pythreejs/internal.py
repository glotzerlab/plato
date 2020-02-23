import numpy as np
import pythreejs

from ... import math

class ThreeJSPrimitive:
    @property
    def threejs_primitive(self):
        try:
            return self._threejs_primitive
        except AttributeError:
            self._threejs_primitive = self._make_threejs_primitive()
            self.update_arrays()
        return self._threejs_primitive

    def _make_threejs_primitive(self):
        geometry = pythreejs.BufferGeometry()
        material = pythreejs.MeshStandardMaterial(
            vertexColors=pythreejs.enums.Colors.VertexColors, metalness=0.05, roughness=.9)
        result = pythreejs.Mesh(geometry, material)

        return result

    def update_arrays(self):
        pass

    def _finalize_primitive_arrays(self, positions, orientations, colors,
                                   images, normals, indices):
        if orientations is not None:
            images = math.quatrot(orientations, images) + positions
            if normals is not None:
                normals = math.quatrot(orientations, normals)
        else:
            images = images + positions

        unfolded_shape = positions.shape[:-1]
        indices = (np.arange(unfolded_shape[0])[:, np.newaxis, np.newaxis]*unfolded_shape[1] +
                   indices)
        indices = indices.reshape((-1,)).astype(np.uint32)

        prim = self.threejs_primitive

        colors = colors.astype(np.float32).reshape((-1, 4))
        if colors[0, 3] < 1 and np.allclose(colors[:, 3], colors[0, 3]):
            # If all colors have the same alpha, enable material transparency
            prim.material.transparent = True
            prim.material.depthWrite = False
            prim.material.opacity = colors[0, 3]

        attribs = dict(position=pythreejs.BufferAttribute(images.astype(np.float32).reshape((-1, 3))),
                       color=pythreejs.BufferAttribute(colors),
                       index=pythreejs.BufferAttribute(indices))
        if normals is not None:
            attribs['normal'] = pythreejs.BufferAttribute(normals.astype(np.float32).reshape((-1, 3)))

        prim.geometry.attributes = attribs

        prim.geometry.exec_three_obj_method('computeVertexNormals')
        prim.geometry.exec_three_obj_method('normalizeNormals')

        self._dirty_attributes.clear()
