import itertools

import numpy as np

from ... import mesh
from .internal import GLPrimitive, GLShapeDecorator
from ... import draw
from ..internal import ShapeAttribute
from ..Scene import DEFAULT_DIRECTIONAL_LIGHTS

@GLShapeDecorator
class ConvexSpheropolyhedra(draw.ConvexSpheropolyhedra, GLPrimitive):
    __doc__ = draw.ConvexSpheropolyhedra.__doc__

    shaders = {}

    shaders['vertex'] = """
       uniform mat4 camera;
       uniform vec4 rotation;
       uniform vec3 translation;
       uniform int transparency_mode;

       attribute vec4 orientation;
       attribute vec4 color;
       attribute vec3 position;
       attribute vec3 normal;
       attribute vec3 inner_image;
       attribute vec3 image;
       attribute vec4 shape_id;

       varying vec4 v_color;
       varying vec3 v_normal;
       varying vec3 v_imageDelta;
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
           vec3 vertexPos = position + rotate(image, orientation);
           vertexPos = rotate(vertexPos, rotation) + translation;
           vec4 screenPosition = camera * vec4(vertexPos, 1.0);

           int should_discard = 0;
           should_discard += int(transparency_mode < 0 && color.a < 1.0);
           should_discard += int(transparency_mode > 0 && color.a >= 1.0);
           if(should_discard > 0)
               screenPosition = vec4(2.0, 2.0, 2.0, 2.0);

           // transform to screen coordinates
           gl_Position = screenPosition;
           v_color = color;
           v_normal = rotate(normal, quatquat(rotation, orientation));
           v_imageDelta = rotate(image - inner_image, quatquat(rotation, orientation));
           v_position = vertexPos;
           v_shape_id = shape_id;
       }
       """

    shaders['fragment'] = """
       #define M_PI 3.1415926535897932384626433832795

       varying vec4 v_color;
       varying vec3 v_normal;
       varying vec3 v_imageDelta;
       varying vec3 v_position;

       uniform mat4 camera;
       uniform float radius;
       // base light level
       uniform float ambientLight;
       // (x, y, z) direction*intensity
       uniform vec3 diffuseLight[NUM_DIFFUSELIGHT];
       uniform int transparency_mode;
       uniform float light_levels;

       void main()
       {
           vec3 normal = v_normal;
           float deltasq = dot(v_imageDelta, v_imageDelta);
           vec3 tangent = v_imageDelta - dot(v_imageDelta, v_normal)*v_normal;
           float tangentsq = dot(tangent, tangent);

           if(tangentsq > 1e-6*radius*radius)
           {
               float lam = sqrt(tangentsq)/radius;
               float scaledRadius = radius*camera[2][2];
               normal = v_imageDelta/sqrt(deltasq);
           }
           else if(deltasq <= radius*radius*(1.0 + 1e-5))
           {
               normal = v_normal;
           }
           else discard;

           float light = ambientLight;
           for(int i = 0; i < NUM_DIFFUSELIGHT; ++i)
               light += max(0.0, -dot(normal, diffuseLight[i]));

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
               gl_FragColor = vec4(v_color.xyz*light, v_color.w);
           else if(transparency_mode == 1)
               gl_FragColor = vec4(v_color.rgb * alpha * light, alpha) * weight;
           else
               gl_FragColor = vec4(alpha);
       }
       """

    shaders['fragment_plane'] = """
       #define M_PI 3.1415926535897932384626433832795

       varying vec3 v_normal;
       varying vec3 v_position;
       varying vec3 v_imageDelta;

       uniform mat4 camera;
       uniform float radius;
       uniform float render_positions = 0.0;

       void main()
       {
           vec3 normal = v_normal;
           float deltasq = dot(v_imageDelta, v_imageDelta);
           vec3 tangent = v_imageDelta - dot(v_imageDelta, v_normal)*v_normal;
           float tangentsq = dot(tangent, tangent);

           if(tangentsq > 1e-6*radius*radius)
           {
               float lam = sqrt(tangentsq)/radius;
               float scaledRadius = radius*camera[2][2];
               normal = v_imageDelta/sqrt(deltasq);
           }
           else if(deltasq <= radius*radius*(1.0 + 1e-5))
           {
               normal = v_normal;
           }
           else discard;

           if(render_positions > 0.5)
               gl_FragColor = vec4(gl_FragCoord.xyz, 1.0);
           else if(render_positions < -0.5)
               gl_FragColor = 0.5 + 0.5*vec4(normal.xyz, 1.0);
           else // Store the plane equation as a color
               gl_FragColor = vec4(normal, dot(normal, v_position.xyz));
       }
       """

    shaders['fragment_pick'] = """
       uniform float radius;
       uniform vec4 pick_prim_index;

       varying vec3 v_normal;
       varying vec3 v_imageDelta;
       varying vec4 v_shape_id;

       void main()
       {
           vec3 normal = v_normal;
           float deltasq = dot(v_imageDelta, v_imageDelta);
           vec3 tangent = v_imageDelta - dot(v_imageDelta, v_normal)*v_normal;
           float tangentsq = dot(tangent, tangent);

           if(tangentsq > 1e-6*radius*radius)
           {
           }
           else if(deltasq <= radius*radius*(1.0 + 1e-5))
           {
           }
           else discard;

           gl_FragColor = pick_prim_index + v_shape_id;
       }
       """

    _vertex_attribute_names = ['shape_id', 'position', 'orientation', 'color', 'image', 'inner_image', 'normal']

    _GL_UNIFORMS = list(itertools.starmap(ShapeAttribute, [
        ('camera', np.float32, np.eye(4), 2, False,
         'Internal: 4x4 Camera matrix for world projection'),
        ('radius', np.float32, 1, 0, False,
         'Rounding radius to be applied to all shapes'),
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
         'Number of light levels to quantize to (0: disable)')
        ]))

    def __init__(self, *args, **kwargs):
        GLPrimitive.__init__(self)
        draw.ConvexSpheropolyhedra.__init__(self, *args, **kwargs)

    def update_arrays(self):
        if 'vertices' in self._dirty_attributes:
            vertices = self.vertices
            if len(vertices) < 4:
                vertices = np.concatenate([vertices,
                    [(-1, -1, -1), (1, 1, -1), (1, -1, 1), (-1, 1, 1)]], axis=0)
            (image, inner_image, normal, indices) = mesh.convexSpheropolyhedronMesh(
                vertices, radius=self.radius)
            self._gl_attributes['image'] = image
            self._gl_attributes['inner_image'] = inner_image
            self._gl_attributes['normal'] = normal
            self._gl_attributes['indices'] = indices

        try:
            for name in self._dirty_attributes:
                if name == 'vertices':
                    for quantity in ['image', 'inner_image', 'normal', 'indices']:
                        self._gl_vertex_arrays[quantity][:] = self._gl_attributes[quantity][np.newaxis]
                        self._dirty_vertex_attribs.add(quantity)
                else:
                    self._gl_vertex_arrays[name][:] = self._attributes[name]
                    self._dirty_vertex_attribs.add(name)
        except (ValueError, KeyError):
            shape_ids = np.arange(len(self), dtype=np.uint32).view(np.uint8).reshape((-1, 4))
            shape_ids = shape_ids.astype(np.float32)/255

            vertex_arrays = mesh.unfoldProperties(
                [shape_ids, self.positions, self.orientations, self.colors],
                [self._gl_attributes[name] for name in ['image', 'inner_image', 'normal']])

            unfolded_shape = vertex_arrays[0].shape[:-1]
            indices = (np.arange(unfolded_shape[0])[:, np.newaxis, np.newaxis]*unfolded_shape[1] +
                       self._gl_attributes['indices'])
            indices = indices.reshape((-1, 3))

            self._finalize_array_updates(indices, vertex_arrays)

        self._dirty_attributes.clear()
