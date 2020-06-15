import itertools

import numpy as np

from ... import mesh
from .internal import GLPrimitive, GLShapeDecorator
from ... import draw
from ..internal import ShapeAttribute
from ..Scene import DEFAULT_DIRECTIONAL_LIGHTS

@GLShapeDecorator
class Mesh(draw.Mesh, GLPrimitive):
    __doc__ = draw.Mesh.__doc__

    shaders = {}

    shaders['vertex'] = """
       uniform mat4 camera;
       uniform vec4 rotation;
       uniform vec3 translation;
       uniform vec3 diffuseLight[NUM_DIFFUSELIGHT];
       uniform float shape_color_fraction;

       attribute vec4 color;
       attribute vec3 normal;
       attribute vec3 image;
       attribute vec3 position;
       attribute vec4 orientation;
       attribute vec4 shape_color;
       attribute vec4 shape_id;

       varying vec4 v_color;
       varying vec3 v_normal;
       varying float v_light[NUM_DIFFUSELIGHT];
       varying vec3 v_position;
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

       void main()
       {
           vec3 vertexPos = image;
           vertexPos = rotate(vertexPos, orientation) + position;
           vertexPos = rotate(vertexPos, rotation) + translation;
           vec4 screenPosition = camera * vec4(vertexPos, 1.0);
           vec3 rotatedNormal = rotate(normal, orientation);
           rotatedNormal = rotate(rotatedNormal, rotation);

           // transform to screen coordinates
           gl_Position = screenPosition;
           v_color = mix(color, shape_color, shape_color_fraction);
           v_normal = rotatedNormal;
           for(int i = 0; i < NUM_DIFFUSELIGHT; ++i)
               v_light[i] = -dot(rotatedNormal, diffuseLight[i]);
           v_position = vertexPos;
           v_shape_id = shape_id;
       }
       """

    shaders['fragment'] = """
       varying vec4 v_color;
       varying vec3 v_normal;
       varying vec3 v_position;
       varying float v_light[NUM_DIFFUSELIGHT];

       // base light level
       uniform float ambientLight;
       uniform int transparency_mode;
       uniform float light_levels;

       void main()
       {
           float light = ambientLight;
           for(int i = 0; i < NUM_DIFFUSELIGHT; ++i)
               light += max(0.0, v_light[i]);

           if(light_levels > 0.0)
           {
               light *= light_levels;
               light = floor(light);
               light /= light_levels;
           }

           float z = abs(v_position.z);
           float alpha = v_color.a;
           float weight = alpha*max(3e3*pow(
               (1.0 - gl_FragCoord.z), 3.0), 1e-2);

           if(transparency_mode < 1)
           {
               // Mesh doesn't discard based on transparency_mode + alpha
               // in the vertex shader, so do it here instead
               if(transparency_mode < 0 && alpha < 1.0)
                   discard;
               gl_FragColor = vec4(v_color.xyz*light, v_color.w);
           }
           else if(transparency_mode == 1)
               gl_FragColor = vec4(v_color.rgb*alpha*light, alpha)*weight;
           else
               gl_FragColor = vec4(alpha);
       }
       """

    shaders['fragment_plane'] = """
       varying vec4 v_color;
       varying vec3 v_normal;
       varying vec3 v_position;

       uniform mat4 camera;
       // base light level
       uniform float render_positions;

       void main()
       {
           if(render_positions > 0.5)
               gl_FragColor = vec4(gl_FragCoord.xyz, 1.0);
           else if(render_positions < -0.5)
               gl_FragColor = vec4(abs(v_normal.x), abs(v_normal.y), abs(v_normal.z), 1.0);
           else // Store the plane equation as a color
               gl_FragColor = vec4(v_normal, dot(v_normal, v_position.xyz));
       }
       """

    shaders['fragment_pick'] = """
       uniform mat4 camera;
       uniform vec4 pick_prim_index;

       varying vec4 v_shape_id;

       void main()
       {
           gl_FragColor = pick_prim_index + v_shape_id;
       }
       """

    _vertex_attribute_names = ['shape_id', 'position', 'orientation', 'shape_color', 'color', 'normal', 'image']

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
        ('shape_color_fraction', np.float32, 0, 0, False,
         'Fraction of a vertex\'s color that should be assigned based on shape_colors')
        ]))

    def __init__(self, *args, **kwargs):
        GLPrimitive.__init__(self)
        draw.Mesh.__init__(self, *args, **kwargs)

    def update_arrays(self):
        if 'vertices' in self._dirty_attributes:
            normal = mesh.computeNormals_(self.vertices, self.indices)

            self._gl_attributes['image'] = self.vertices
            self._gl_attributes['normal'] = normal
            self._gl_attributes['indices'] = self.indices

        if 'shape_colors' in self._dirty_attributes:
            if len(self._attributes['colors']) < len(self._attributes['vertices']):
                Ntile = int(np.ceil(len(self._attributes['vertices'])/
                                    len(self._attributes['colors'])))
                new_colors = np.tile(self._attributes['colors'], (Ntile, 1))
                self.colors = new_colors

        if 'colors' in self._dirty_attributes:
            if len(self._attributes['shape_colors']) < len(self._attributes['positions']):
                Ntile = int(np.ceil(len(self._attributes['positions'])/
                                    len(self._attributes['shape_colors'])))
                new_colors = np.tile(self._attributes['shape_colors'], (Ntile, 1))
                self.shape_colors = new_colors

        try:
            for name in self._dirty_attributes:
                self._gl_vertex_arrays[name][:] = self._attributes[name]
                self._dirty_vertex_attribs.add(name)
        except (ValueError, KeyError):
            shape_ids = np.arange(len(self), dtype=np.uint32).view(np.uint8).reshape((-1, 4))
            shape_ids = shape_ids.astype(np.float32)/255

            vertex_arrays = mesh.unfoldProperties(
                [shape_ids, self.positions, self.orientations, self.shape_colors],
                [self.colors] + [self._gl_attributes[name] for name in ['normal', 'image']]
                )

            unfolded_shape = vertex_arrays[0].shape[:-1]
            indices = (np.arange(unfolded_shape[0])[:, np.newaxis, np.newaxis]*unfolded_shape[1] +
                       self._gl_attributes['indices'][np.newaxis, :, :]).reshape((-1, 3))

            self._finalize_array_updates(indices, vertex_arrays)

        self._dirty_attributes.clear()
