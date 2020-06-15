import itertools

import numpy as np

from ... import mesh
from .internal import GLPrimitive, GLShapeDecorator
from ... import draw
from ..internal import ShapeAttribute

@GLShapeDecorator
class Voronoi(draw.Voronoi, GLPrimitive):
    __doc__ = draw.Voronoi.__doc__

    shaders = {}

    shaders['vertex'] = """
       uniform mat4 camera;
       uniform vec4 rotation;
       uniform vec3 translation;
       uniform float radius;

       attribute vec4 color;
       attribute vec2 position;
       attribute vec3 image;
       attribute vec4 shape_id;

       varying vec4 v_color;
       varying vec2 v_position;
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
           vec2 vertexPos = position + image.xy*radius;
           vertexPos = rotate(vertexPos, rotation) + translation.xy;
           vec4 screenPosition = camera * vec4(vertexPos, 0, 1.0);
           screenPosition.z = image.z;

           // transform to screen coordinates
           gl_Position = screenPosition;
           v_position = position + image.xy*radius;
           v_color = color;
           v_shape_id = shape_id;
       }
       """

    shaders['fragment'] = """
       uniform mat2 clip_extent;

       varying vec4 v_color;
       varying vec2 v_position;

       void main()
       {
           vec2 boundaries = clip_extent*v_position;

           if(boundaries.x > 1.0 || boundaries.y > 1.0 ||
              boundaries.x < -1.0 || boundaries.y < -1.0)
               discard;

           gl_FragColor = v_color;
       }
       """

    shaders['fragment_pick'] = """
       uniform mat2 clip_extent;
       uniform vec4 pick_prim_index;

       varying vec2 v_position;
       varying vec4 v_shape_id;

       void main()
       {
           vec2 boundaries = clip_extent*v_position;

           if(boundaries.x > 1.0 || boundaries.y > 1.0 ||
              boundaries.x < -1.0 || boundaries.y < -1.0)
               discard;

           gl_FragColor = pick_prim_index + v_shape_id;
       }
       """

    _vertex_attribute_names = ['shape_id', 'position', 'color', 'image']

    _GL_UNIFORMS = list(itertools.starmap(ShapeAttribute, [
        ('camera', np.float32, np.eye(4), 2, False,
         'Internal: 4x4 Camera matrix for world projection'),
        ('rotation', np.float32, (1, 0, 0, 0), 1, False,
         'Internal: Rotation to be applied to each scene as a quaternion'),
        ('translation', np.float32, (0, 0, 0), 1, False,
         'Internal: Translation to be applied to the scene'),
        ('radius', np.float32, 64, 0, False,
         'Maximum distance between displayed points'),
        ('clip_extent', np.float32, np.zeros((2, 2)), 2, False,
         'Matrix specifying areas to not display when dot(clip_extent, position) is outside [-1, 1]')
        ]))

    def __init__(self, *args, **kwargs):
        self.num_vertices = 32
        GLPrimitive.__init__(self)
        draw.Voronoi.__init__(self, *args, **kwargs)

    def update_arrays(self):
        try:
            for name in self._dirty_attributes:
                self._gl_vertex_arrays[name][:] = self._attributes[name]
                self._dirty_vertex_attribs.add(name)
        except (ValueError, KeyError):
            # wrap around to beginning of circle, but also have vertex 0
            # be (0, 0), so we still end up with num_vertices vertices in
            # total
            thetas = np.linspace(0, 2*np.pi, self.num_vertices, endpoint=True)
            vertices = np.array([np.cos(thetas), np.sin(thetas), np.ones_like(thetas)], dtype=np.float32).T
            vertices[0] = (0, 0, 0)

            triangleIndices = np.zeros((self.num_vertices - 1, 3), dtype=np.uint32)
            triangleIndices[:, 1] = np.arange(self.num_vertices - 1) + 1
            triangleIndices[:, 2] = np.arange(self.num_vertices - 1) + 2
            triangleIndices[-1, 2] = 1

            shape_ids = np.arange(len(self), dtype=np.uint32).view(np.uint8).reshape((-1, 4))
            shape_ids = shape_ids.astype(np.float32)/255

            vertex_arrays = mesh.unfoldProperties(
                [shape_ids, self.positions, self.colors],
                [vertices])

            unfolded_shape = vertex_arrays[0].shape[:-1]
            indices = (np.arange(unfolded_shape[0])[:, np.newaxis, np.newaxis]*unfolded_shape[1] +
                       triangleIndices)
            indices = indices.reshape((-1, 3))

            self._finalize_array_updates(indices, vertex_arrays)

        self._dirty_attributes.clear()
