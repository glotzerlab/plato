import itertools

import numpy as np

from ... import mesh
from .internal import GLPrimitive, GLShapeDecorator
from ... import draw
from ..internal import ShapeAttribute
from ..Scene import DEFAULT_DIRECTIONAL_LIGHTS

@GLShapeDecorator
class SphereUnions(draw.SphereUnions, GLPrimitive):
    __doc__ = draw.SphereUnions.__doc__

    shaders = {}

    shaders['vertex'] = """
       uniform mat4 camera;
       uniform vec4 rotation;
       uniform vec3 translation;
       uniform int transparency_mode;

       attribute vec4 color;
       attribute vec3 position;
       attribute vec4 orientation;
       attribute vec3 point;
       attribute vec2 image;
       attribute float radius;
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

       void main()
       {
           vec3 vertexPos = position;
           vec2 localPos = image*radius;
           vec3 pointPos = point;
           vertexPos = rotate(vertexPos, rotation) + rotate(rotate(pointPos, orientation),rotation) + vec3(localPos, 0.0) + translation;
           vec4 screenPosition = camera * vec4(vertexPos, 1.0);

           int should_discard = 0;
           should_discard += int(transparency_mode < 0 && color.a < 1.0);
           should_discard += int(transparency_mode > 0 && color.a >= 1.0);
           if(should_discard > 0)
               screenPosition = vec4(2.0, 2.0, 2.0, 2.0);

           // transform to screen coordinates
           gl_Position = screenPosition;
           v_color = color;
           v_image = localPos;
           v_radius = radius;
           v_position = vertexPos;
           v_depth = vertexPos.z;
           v_shape_id = shape_id;
       }
       """

    shaders['fragment'] = """
#ifdef GL_ES
       precision highp float;
#endif

       // base light level
       uniform float ambientLight;
       // (x, y, z) direction*intensity
       uniform vec3 diffuseLight[NUM_DIFFUSELIGHT];
       uniform int transparency_mode;
       uniform mat4 camera;
       uniform float light_levels;
       uniform float outline;

       varying vec4 v_color;
       varying vec2 v_image;
       varying float v_radius;
       varying float v_depth;

       void main()
       {
           float rsq = dot(v_image, v_image);
           float Rsq = v_radius*v_radius;

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

           if(r > v_radius) discard;

           vec3 r_local = vec3(v_image.xy, sqrt(Rsq - rsq));
           vec3 normal = normalize(r_local);
           float light = ambientLight;
           for(int i = 0; i < NUM_DIFFUSELIGHT; ++i)
               light += max(0.0, -dot(normal, diffuseLight[i]));

           if(light_levels > 0.0)
           {
               light *= light_levels;
               light = floor(light);
               light /= light_levels;
           }

           vec4 color = vec4(v_color.xyz*lambda1*light, v_color.w);

           #ifndef WEBGL
           float depth = v_depth + r_local.z;
           gl_FragDepth = 0.5*(camera[2][2]*depth + camera[3][2] +
               camera[2][3]*depth + camera[3][3])/(camera[2][3]*depth + camera[3][3]);
           #endif

           float z = abs(v_depth);
           float alpha = color.a;
           float weight = alpha*max(3e3*pow(
               (1.0 - gl_FragCoord.z), 3.0), 1e-2);

           if(transparency_mode < 1)
               gl_FragColor = color;
           else if(transparency_mode == 1)
               gl_FragColor = vec4(color.rgb*alpha, alpha)*weight;
           else
               gl_FragColor = vec4(alpha);
       }
       """

    shaders['fragment_plane'] = """
       // base light level
       uniform mat4 camera;
       uniform float render_positions = 0.0;

       varying vec3 v_position;
       varying vec2 v_image;
       varying float v_radius;
       varying float v_depth;

       void main()
       {
           float rsq = dot(v_image, v_image);
           float Rsq = v_radius*v_radius;

           if(rsq > Rsq)
               discard;

           vec3 r_local = vec3(v_image.xy, sqrt(Rsq - rsq));
           vec3 normal = normalize(r_local);
           #ifndef WEBGL
           float depth = v_depth + r_local.z;
           gl_FragDepth = 0.5*(camera[2][2]*depth + camera[3][2] +
               camera[2][3]*depth + camera[3][3])/(camera[2][3]*depth + camera[3][3]);
           #endif

           if(render_positions > 0.5)
               gl_FragColor = vec4(gl_FragCoord.xyz, 1.0);
           else if(render_positions < -0.5)
               gl_FragColor = 0.5 + 0.5*vec4(normal.xyz, 1.0);
           else // Store the plane equation as a color
               gl_FragColor = vec4(normal, dot(normal, v_position.xyz));
       }
       """

    shaders['fragment_pick'] = """
       uniform mat4 camera;
       uniform vec4 pick_prim_index;

       varying vec3 v_position;
       varying vec2 v_image;
       varying float v_radius;
       varying float v_depth;
       varying vec4 v_shape_id;

       void main()
       {
           float rsq = dot(v_image, v_image);
           float Rsq = v_radius*v_radius;

           if(rsq > Rsq)
               discard;

           vec3 r_local = vec3(v_image.xy, sqrt(Rsq - rsq));
           vec3 normal = normalize(r_local);
           #ifndef WEBGL
           float depth = v_depth + r_local.z;
           gl_FragDepth = 0.5*(camera[2][2]*depth + camera[3][2] +
               camera[2][3]*depth + camera[3][3])/(camera[2][3]*depth + camera[3][3]);
           #endif

           gl_FragColor = pick_prim_index + v_shape_id;
       }
       """

    _vertex_attribute_names = ['shape_id', 'position', 'orientation', 'color', 'point', 'radius', 'image']

    _GL_UNIFORMS = list(itertools.starmap(ShapeAttribute, [
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
        draw.SphereUnions.__init__(self, *args, **kwargs)

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
