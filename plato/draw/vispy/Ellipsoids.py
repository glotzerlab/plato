import itertools

import numpy as np

from ... import mesh
from .internal import GLPrimitive, GLShapeDecorator
from .Spheres import Spheres
from ... import draw
from ..internal import ShapeAttribute
from ..Scene import DEFAULT_DIRECTIONAL_LIGHTS

@GLShapeDecorator
class Ellipsoids(draw.Ellipsoids, GLPrimitive):
    __doc__ = draw.Ellipsoids.__doc__

    shaders = {}

    shaders['vertex'] = """
       uniform mat4 camera;
       uniform vec4 rotation;
       uniform vec3 translation;
       uniform float a;
       uniform float b;
       uniform float c;
       uniform int transparency_mode;

       attribute vec4 color;
       attribute vec4 orientation;
       attribute vec3 position;
       attribute vec2 image;
       attribute vec4 shape_id;

       varying vec4 v_color;
       varying vec3 v_position;
       varying vec2 v_image;
       varying float v_radius;
       varying float v_depth;
       varying vec4 v_shape_id;

       vec3 rotate(vec3 point, vec4 quat)
       {
           vec3 result = (quat.x*quat.x - dot(quat.yzw, quat.yzw))*point;
           result += 2.0*quat.x*cross(quat.yzw, point);
           result += 2.0*dot(quat.yzw, point)*quat.yzw;
           return result;
       }

       vec4 quatquat(vec4 a, vec4 b)
       {
           float real = a.x*b.x - dot(a.yzw, b.yzw);
           vec3 imag = a.x*b.yzw + b.x*a.yzw + cross(a.yzw, b.yzw);
           return vec4(real, imag);
       }

       mat3 quatmat(vec4 quat)
       {
           // rgba -> real, x, y, z
           vec3 col_a, col_b, col_c;
           col_a = vec3(1.0 - 2.0*quat.b*quat.b - 2.0*quat.a*quat.a,
                        2.0*quat.g*quat.b + 2.0*quat.a*quat.r,
                        2.0*quat.g*quat.a - 2.0*quat.b*quat.r);
           col_b = vec3(2.0*quat.g*quat.b - 2.0*quat.a*quat.r,
                        1.0 - 2.0*quat.g*quat.g - 2.0*quat.a*quat.a,
                        2.0*quat.b*quat.a + 2.0*quat.g*quat.r);
           col_c = vec3(2.0*quat.g*quat.a + 2.0*quat.b*quat.r,
                        2.0*quat.b*quat.a - 2.0*quat.g*quat.r,
                        1.0 - 2.0*quat.g*quat.g - 2.0*quat.b*quat.b);
           return mat3(col_a, col_b, col_c);
       }

       vec4 conj(vec4 quat)
       {
           return vec4(-quat.x, quat.yzw);
       }

       void main()
       {
           vec4 fullRotation = quatquat(rotation, orientation);
           mat3 fullRotationmat = quatmat(fullRotation);
           mat3 ellipsoid = mat3(vec3(a, 0.0, 0.0),
               vec3(0.0, b, 0.0),
               vec3(0.0, 0.0, c));
           ellipsoid = fullRotationmat*ellipsoid;

           vec3 local_image = ellipsoid*rotate(vec3(image, 0.0), conj(fullRotation));

           vec3 vertexPos = position;
           vertexPos = rotate(vertexPos, rotation) + translation;
           vertexPos += local_image;
           vec4 screenPosition = camera * vec4(vertexPos, 1.0);

           int should_discard = 0;
           should_discard += int(transparency_mode < 0 && color.a < 1.0);
           should_discard += int(transparency_mode > 0 && color.a >= 1.0);
           if(should_discard > 0)
               screenPosition = vec4(2.0, 2.0, 2.0, 2.0);

           // transform to screen coordinates
           gl_Position = screenPosition;
           v_color = color;
           v_position = vertexPos;
           v_image = image;
           v_radius = 1.0;
           v_depth = vertexPos.z;
           v_shape_id = shape_id;
       }
       """

    shaders['fragment'] = Spheres.shaders['fragment']

    shaders['fragment_plane'] = Spheres.shaders['fragment_plane']

    shaders['fragment_pick'] = Spheres.shaders['fragment_pick']

    _vertex_attribute_names = ['shape_id', 'position', 'orientation', 'color', 'image']

    _GL_UNIFORMS = list(itertools.starmap(ShapeAttribute, [
        ('a', np.float32, .5, 0, False,
         'Radius in the x-direction'),
        ('b', np.float32, .5, 0, False,
         'Radius in the y-direction'),
        ('c', np.float32, .5, 0, False,
         'Radius in the z-direction'),
        ('camera', np.float32, np.eye(4), 2, False,
         'Internal: 4x4 Camera matrix for world projection'),
        ('ambientLight', np.float32, .25, 0, False,
         'Internal: Ambient (minimum) light level for all surfaces'),
        ('diffuseLight[]', np.float32, DEFAULT_DIRECTIONAL_LIGHTS, 2, False,
         'Internal: Diffuse light direction*magnitude'),
        ('rotation', np.float32, (1, 0, 0, 0), 1, False,
         'Internal: Rotation to be applied to each scene as a quaternion'),
        ('translation', np.float32, (0, 0, 0), 1, False,
         'Internal: Translation to be applied to the scene'),
        ('transparency_mode', np.int32, 0, 0, False,
         'Internal: Transparency stage (<0: opaque, 0: all, 1: '
         'translucency stage 1, 2: translucency stage 2)'),
        ('light_levels', np.float32, 0, 0, False,
         'Number of light levels to quantize to (0: disable)'),
        ('outline', np.float32, 0, 0, False,
         'Outline for all particles')
        ]))

    def __init__(self, *args, **kwargs):
        GLPrimitive.__init__(self)
        draw.Ellipsoids.__init__(self, *args, **kwargs)

    def update_arrays(self):
        try:
            for name in self._dirty_attributes:
                self._gl_vertex_arrays[name][:] = self._attributes[name]
                self._dirty_vertex_attribs.add(name)
        except (ValueError, KeyError):
            # vertices for a square patch
            image = np.array([[-1, -1], [-1, 1], [1, -1], [1, 1]], dtype=np.float32)

            shape_ids = np.arange(len(self), dtype=np.uint32).view(np.uint8).reshape((-1, 4))
            shape_ids = shape_ids.astype(np.float32)/255

            vertex_arrays = mesh.unfoldProperties(
                [shape_ids, self.positions, self.orientations, self.colors],
                [image])

            unfolded_shape = vertex_arrays[0].shape[:-1]
            indices = (np.arange(unfolded_shape[0])[:, np.newaxis, np.newaxis]*unfolded_shape[1] +
                       np.array([(0, 2, 3), (3, 1, 0)], dtype=np.uint32))
            indices = indices.reshape((-1, 3))

            self._finalize_array_updates(indices, vertex_arrays)

        self._dirty_attributes.clear()
