import itertools

import numpy as np

from ... import mesh
from .internal import GLPrimitive, GLShapeDecorator
from ... import draw
from ..internal import ShapeAttribute

@GLShapeDecorator
class Spheropolygons(draw.Spheropolygons, GLPrimitive):
    __doc__ = draw.Spheropolygons.__doc__

    shaders = {}

    shaders['vertex'] = """
       uniform mat4 camera;
       uniform vec4 rotation;
       uniform vec3 translation;
       uniform float radius;

       attribute vec4 color;
       attribute vec2 position;
       attribute vec2 image;
       attribute vec2 inner_image;
       attribute vec4 orientation;
       attribute vec4 shape_id;

       varying vec4 v_color;
       varying vec2 v_imageDelta;
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
           vec2 real_image = (image - inner_image)*radius + inner_image;
           vec2 vertexPos = position + rotate(real_image, orientation);
           vertexPos = rotate(vertexPos, rotation) + translation.xy;
           vec4 screenPosition = camera * vec4(vertexPos, translation.z, 1.0);

           // transform to screen coordinates
           gl_Position = screenPosition;
           v_color = color;
           v_imageDelta = real_image - inner_image;
           v_shape_id = shape_id;
       }
       """

    shaders['fragment'] = """
       uniform float outline;
       uniform float radius;

       varying vec4 v_color;
       varying vec2 v_imageDelta;

       void main()
       {
           float lambda1 = 1.0;
           float rsq = dot(v_imageDelta, v_imageDelta);
           float r = sqrt(rsq);

           if(outline > 1e-6)
           {
               lambda1 = (radius - r)/outline;
               lambda1 *= lambda1;
               lambda1 *= lambda1;
               lambda1 *= lambda1;
               lambda1 *= lambda1;
               lambda1 = min(lambda1, 1.0);
           }

           float lambda2 = 1.0;
           if(r > radius) discard;
           else if(outline <= 1e-6)
           {
               lambda2 = r/radius;
               lambda2 *= lambda2;
               lambda2 *= lambda2;
               lambda2 *= lambda2;
               lambda2 *= lambda2;
               lambda2 *= lambda2;
               lambda2 *= lambda2;
               lambda2 *= lambda2;
               lambda2 = 1.0 - min(lambda2, 1.0);
           }
           else if(r > radius - outline)
           {
               lambda2 = (r - radius + outline)/outline;
               lambda2 *= lambda2;
               lambda2 *= lambda2;
               lambda2 *= lambda2;
               lambda2 *= lambda2;
               lambda2 = 1.0 - min(lambda2, 1.0);
           }

           gl_FragColor = vec4(lambda1*v_color.xyz, lambda2*v_color.w);
       }
       """

    shaders['fragment_pick'] = """
       uniform float radius;
       uniform vec4 pick_prim_index;

       varying vec2 v_imageDelta;
       varying vec4 v_shape_id;

       void main()
       {
           float rsq = dot(v_imageDelta, v_imageDelta);
           float r = sqrt(rsq);

           if(r > radius) discard;

           gl_FragColor = pick_prim_index + v_shape_id;
       }
       """

    _vertex_attribute_names = ['shape_id', 'position', 'orientation', 'color', 'image', 'inner_image']

    _GL_UNIFORMS = list(itertools.starmap(ShapeAttribute, [
        ('camera', np.float32, np.eye(4), 2, False,
         'Internal: 4x4 Camera matrix for world projection'),
        ('rotation', np.float32, (1, 0, 0, 0), 1, False,
         'Internal: Rotation to be applied to each scene as a quaternion'),
        ('translation', np.float32, (0, 0, 0), 1, False,
         'Internal: Translation to be applied to the scene'),
        ('outline', np.float32, 0, 0, False,
         'Outline width for shapes'),
        ('radius', np.float32, 0, 0, False,
         'Rounding radius for shapes')
        ]))

    def __init__(self, *args, **kwargs):
        GLPrimitive.__init__(self)
        draw.Spheropolygons.__init__(self, *args, **kwargs)

    def update_arrays(self):
        if 'vertices' in self._dirty_attributes:
            vertices = self.vertices
            if len(vertices) < 3:
                thetas = np.linspace(0, 2*np.pi, 3, endpoint=False)
                vertices = np.array([np.cos(thetas), np.sin(thetas)], dtype=np.float32).T

            mesh_ = mesh.spheropolygonMesh(vertices, 1, granularity=2)
            self._gl_attributes['image'] = mesh_.image.astype(np.float32)
            self._gl_attributes['inner_image'] = mesh_.innerImage.astype(np.float32)
            self._gl_attributes['indices'] = mesh_.indices

        try:
            for name in self._dirty_attributes:
                if name == 'vertices':
                    raise ValueError
                else:
                    self._gl_vertex_arrays[name][:] = self._attributes[name]
                    self._dirty_vertex_attribs.add(name)
        except (ValueError, KeyError):
            shape_ids = np.arange(len(self), dtype=np.uint32).view(np.uint8).reshape((-1, 4))
            shape_ids = shape_ids.astype(np.float32)/255

            vertex_arrays = mesh.unfoldProperties(
                [shape_ids, self.positions, self.orientations, self.colors],
                [self._gl_attributes['image'], self._gl_attributes['inner_image']])

            unfolded_shape = vertex_arrays[0].shape[:-1]
            indices = (np.arange(unfolded_shape[0])[:, np.newaxis, np.newaxis]*unfolded_shape[1] +
                       self._gl_attributes['indices'])
            indices = indices.reshape((-1, 3))

            self._finalize_array_updates(indices, vertex_arrays)

        self._dirty_attributes.clear()
