import itertools

import numpy as np

from ... import mesh
from .internal import GLPrimitive, GLShapeDecorator
from ... import draw
from ..internal import ShapeAttribute

@GLShapeDecorator
class DiskUnions(draw.DiskUnions, GLPrimitive):
    __doc__ = draw.DiskUnions.__doc__

    shaders = {}

    shaders['vertex'] = """
       uniform mat4 camera;
       uniform vec4 rotation;
       uniform vec3 translation;
       uniform float outline;

       attribute vec4 color;
       attribute vec2 position;
       attribute vec4 orientation;
       attribute vec2 point;
       attribute vec2 image;
       attribute float radius;
       attribute vec4 shape_id;

       varying vec4 v_color;
       varying vec2 v_image;
       varying float v_radius;
       varying vec4 v_shape_id;

       vec2 rotate(vec2 point, vec4 quat)
       {
           vec3 point3d = vec3(point.xy, 0.0);
           vec3 result = (quat.x*quat.x - dot(quat.yzw, quat.yzw))*point3d;
           result += 2.0*quat.x*cross(quat.yzw, point3d);
           result += 2.0*dot(quat.yzw, point3d)*quat.yzw;
           return result.xy;
       }

       void main()
       {
           vec4 currentColor = color;
           if(outline < 0.0)
               currentColor = vec4(0.0, 0.0, 0.0, color.a);

           vec2 vertexPos = rotate(point, orientation);
           vertexPos += position + radius*image;
           vertexPos = rotate(vertexPos, rotation) + translation.xy;
           vec4 screenPosition = camera * vec4(vertexPos, translation.z, 1.0);

           // transform to screen coordinates
           gl_Position = screenPosition;
           v_color = currentColor;
           v_image = radius*image;
           v_radius = radius;
           v_shape_id = shape_id;
       }
       """

    shaders['fragment'] = """

#ifdef GL_ES
       precision highp float;
#endif

       uniform float outline;

       varying vec4 v_color;
       varying vec2 v_image;
       varying float v_radius;

       void main()
       {
           float rsq = dot(v_image, v_image);

           float r = sqrt(rsq);

           float lambda1 = 1.0;
           if(outline > 1e-6)
           {
               lambda1 = (v_radius - r)/outline;
               lambda1 *= lambda1;
               lambda1 *= lambda1;
               lambda1 *= lambda1;
               lambda1 *= lambda1;
               lambda1 = min(lambda1, 1.0);
           }

           float lambda2 = 1.0;
           if(r > v_radius) discard;
           else if(outline <= 1e-6)
           {
               lambda2 = r/v_radius;
               lambda2 *= lambda2;
               lambda2 *= lambda2;
               lambda2 *= lambda2;
               lambda2 *= lambda2;
               lambda2 *= lambda2;
               lambda2 *= lambda2;
               lambda2 *= lambda2;
               lambda2 = 1.0 - min(lambda2, 1.0);
           }
           else if(r > v_radius - outline)
           {
               lambda2 = (r - v_radius + outline)/outline;
               lambda2 *= lambda2;
               lambda2 *= lambda2;
               lambda2 *= lambda2;
               lambda2 *= lambda2;
               lambda2 = 1.0 - min(lambda2, 1.0);
           }

           gl_FragColor = vec4(v_color.xyz*lambda1, lambda2*v_color.w);
       }
       """

    shaders['fragment_pick'] = """
       uniform vec4 pick_prim_index;

       varying vec2 v_image;
       varying float v_radius;
       varying vec4 v_shape_id;

       void main()
       {
           float rsq = dot(v_image, v_image);

           float r = sqrt(rsq);

           if(r > v_radius) discard;

           gl_FragColor = pick_prim_index + v_shape_id;
       }
       """

    _vertex_attribute_names = ['shape_id', 'position', 'orientation', 'color', 'point', 'radius', 'image']

    _GL_UNIFORMS = list(itertools.starmap(ShapeAttribute, [
        ('camera', np.float32, np.eye(4), 2, False,
         'Internal: 4x4 Camera matrix for world projection'),
        ('rotation', np.float32, (1, 0, 0, 0), 1, False,
         'Internal: Rotation to be applied to each scene as a quaternion'),
        ('translation', np.float32, (0, 0, 0), 1, False,
         'Internal: Translation to be applied to the scene'),
        ('outline', np.float32, 0, 0, False,
         'Outline width for shapes')
        ]))

    def __init__(self, *args, **kwargs):
        GLPrimitive.__init__(self)
        draw.DiskUnions.__init__(self, *args, **kwargs)

    def update_arrays(self):

        try:
            for name in self._dirty_attributes:
                self._gl_vertex_arrays[name][:] = self._attributes[name]
                self._dirty_vertex_attribs.add(name)
        except (ValueError, KeyError):
            # vertices for an equilateral triangle
            triangle = np.array([[2, 0],
                                 [-1, np.sqrt(3)],
                                 [-1, -np.sqrt(3)]], dtype=np.float32)*1.01

            shape_ids = np.arange(len(self), dtype=np.uint32).view(np.uint8).reshape((-1, 4))
            shape_ids = shape_ids.astype(np.float32)/255

            vertex_arrays = mesh.unfoldProperties(
              [shape_ids, self.positions, self.orientations],
              [self.colors, self.points, self.radii.reshape((-1, 1))],
              [triangle])

            unfolded_shape = vertex_arrays[0].shape[:-1]
            indices = np.arange(np.product(unfolded_shape))
            indices = indices.reshape((-1, 3))

            self._finalize_array_updates(indices, vertex_arrays)

        self._dirty_attributes.clear()
