import itertools
import numpy as np
from ... import mesh
from .internal import GLPrimitive, GLShapeDecorator
from ... import draw
from ..internal import ShapeAttribute
from vispy import gloo

@GLShapeDecorator
class Spheres(draw.Spheres, GLPrimitive):
    __doc__ = draw.Spheres.__doc__

    shaders = {}

    shaders['vertex'] = """
       uniform mat4 camera;
       uniform vec4 rotation;
       uniform vec3 translation;
       uniform int transparency_mode;

       attribute vec4 color;
       attribute vec3 position;
       attribute vec2 image;
       attribute float radius;

       varying vec4 v_color;
       varying vec3 v_position;
       varying vec2 v_image;
       varying float v_radius;
       varying float v_depth;

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
           vertexPos = rotate(vertexPos, rotation) + vec3(localPos, 0.0) + translation;
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
       }
       """

    shaders['fragment'] = """
       // base light level
       uniform float ambientLight;
       // (x, y, z) direction*intensity
       uniform vec3 diffuseLight;
       uniform int transparency_mode;
       uniform mat4 camera;
       uniform float light_levels;

       varying vec4 v_color;
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
           float light = max(0.0, -dot(normal, diffuseLight));
           light += ambientLight;

           if(light_levels > 0.0)
           {
               light *= light_levels;
               light = floor(light);
               light /= light_levels;
           }

           #ifndef WEBGL
           float depth = v_depth + r_local.z;
           gl_FragDepth = 0.5*(camera[2][2]*depth + camera[3][2] +
               camera[2][3]*depth + camera[3][3])/(camera[2][3]*depth + camera[3][3]);
           #endif

           float z = abs(v_depth);
           float alpha = v_color.a;
           float weight = alpha*max(3e3*pow(
               (1.0 - gl_FragCoord.z), 3.0), 1e-2);

           if(transparency_mode < 1)
               gl_FragColor = vec4(v_color.xyz*light, v_color.w);
           else if(transparency_mode == 1)
               gl_FragColor = vec4(v_color.rgb*alpha*light, alpha)*weight;
           else
               gl_FragColor = vec4(alpha);
       }
       """

    shaders['fragment_plane'] = """
       // base light level
       uniform float ambientLight;
       // (x, y, z) direction*intensity
       uniform vec3 diffuseLight;
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
           float light = max(0.0, dot(normal, diffuseLight));
           light += ambientLight;
           #ifndef WEBGL
           float depth = v_depth + r_local.z;
           gl_FragDepth = 0.5*(camera[2][2]*depth + camera[3][2] +
               camera[2][3]*depth + camera[3][3])/(camera[2][3]*depth + camera[3][3]);
           #endif

           if(render_positions > 0.5)
               gl_FragColor = vec4(gl_FragCoord.xyz, 1.0);
           else // Store the plane equation as a color
               gl_FragColor = vec4(normal, dot(normal, v_position.xyz));
       }
       """

    _vertex_attribute_names = ['position', 'color', 'radius', 'image']

    _GL_UNIFORMS = list(itertools.starmap(ShapeAttribute, [
        ('camera', np.float32, np.eye(4), 2,
         'Internal: 4x4 Camera matrix for world projection'),
        ('ambientLight', np.float32, .25, 0,
         'Internal: Ambient (minimum) light level for all surfaces'),
        ('diffuseLight', np.float32, (.5, .5, .5), 1,
         'Internal: Diffuse light direction*magnitude'),
        ('rotation', np.float32, (1, 0, 0, 0), 1,
         'Internal: Rotation to be applied to each scene as a quaternion'),
        ('translation', np.float32, (0, 0, 0), 1,
         'Internal: Translation to be applied to the scene'),
        ('transparency_mode', np.int32, 0, 0,
         'Internal: Transparency stage (<0: opaque, 0: all, 1: '
         'translucency stage 1, 2: translucency stage 2)'),
        ('light_levels', np.float32, 0, 0,
         'Number of light levels to quantize to (0: disable)')
        ]))

    def __init__(self, *args, **kwargs):
        GLPrimitive.__init__(self)
        draw.Spheres.__init__(self, *args, **kwargs)

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

            vertex_arrays = mesh.unfoldProperties(
                [self.positions, self.colors, self.radii.reshape((-1, 1))],
                [triangle])

            unfolded_shape = vertex_arrays[0].shape[:-1]
            indices = (np.arange(unfolded_shape[0])[:, np.newaxis, np.newaxis]*unfolded_shape[1] +
                       np.array([[0, 1, 2]], dtype=np.uint32))
            indices = indices.reshape((-1, 3))

            self._finalize_array_updates(indices, vertex_arrays)

        self._dirty_attributes.clear()
