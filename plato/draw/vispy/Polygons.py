import itertools

import numpy as np

from ... import geometry
from ... import mesh
from .internal import GLPrimitive, GLShapeDecorator
from ... import draw
from ..internal import ShapeAttribute

@GLShapeDecorator
class Polygons(draw.Polygons, GLPrimitive):
    __doc__ = draw.Polygons.__doc__

    shaders = {}

    shaders['vertex'] = """
       uniform mat4 camera;
       uniform vec4 rotation;
       uniform vec3 translation;
       uniform float outline;

       attribute vec4 color;
       attribute vec2 position;
       attribute vec2 image;
       attribute vec2 outline_image;
       attribute vec4 orientation;
       attribute vec4 shape_id;

       varying vec4 v_color;
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
           vec2 currentImage = mix(image, outline_image, max(0.0, outline));
           vec4 currentColor = color;
           if(outline < 0.0)
               currentColor = vec4(0.0, 0.0, 0.0, color.a);

           vec2 vertexPos = position + rotate(currentImage, orientation);
           vertexPos = rotate(vertexPos, rotation) + translation.xy;
           vec4 screenPosition = camera * vec4(vertexPos, translation.z, 1.0);

           // transform to screen coordinates
           gl_Position = screenPosition;
           v_color = currentColor;
           v_shape_id = shape_id;
       }
       """

    shaders['fragment'] = """
       varying vec4 v_color;

       void main()
       {
           gl_FragColor = v_color;
       }
       """

    shaders['fragment_pick'] = """
       uniform vec4 pick_prim_index;

       varying vec4 v_shape_id;

       void main()
       {
           gl_FragColor = pick_prim_index + v_shape_id;
       }
       """

    _vertex_attribute_names = ['shape_id', 'position', 'orientation', 'color', 'image', 'outline_image']

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
        draw.Polygons.__init__(self, *args, **kwargs)

    def update_arrays(self):
        if 'vertices' in self._dirty_attributes:
            vertices = self.vertices
            if len(vertices) < 3:
                thetas = np.linspace(0, 2*np.pi, 3, endpoint=False)
                vertices = np.array([np.cos(thetas), np.sin(thetas)], dtype=np.float32).T

            polygon = geometry.Polygon(vertices)
            self._gl_attributes['triangulation'] = geometry.Outline(polygon, 1.0)
            self._gl_attributes['indices'] = self._gl_attributes['triangulation'].outer.triangleIndices

        try:
            for name in self._dirty_attributes:
                if name == 'vertices':
                    raise ValueError
                else:
                    self._gl_vertex_arrays[name][:] = self._attributes[name]
                    self._dirty_vertex_attribs.add(name)
        except (ValueError, KeyError):
            vertices = self._gl_attributes['triangulation'].outer.vertices
            outline_vertices = self._gl_attributes['triangulation'].inner.vertices

            shape_ids = np.arange(len(self), dtype=np.uint32).view(np.uint8).reshape((-1, 4))
            shape_ids = shape_ids.astype(np.float32)/255

            vertex_arrays = mesh.unfoldProperties(
                [shape_ids, self.positions, self.orientations, self.colors],
                [vertices, outline_vertices])

            unfolded_shape = vertex_arrays[0].shape[:-1]
            indices = (np.arange(unfolded_shape[0])[:, np.newaxis, np.newaxis]*unfolded_shape[1] +
                       self._gl_attributes['indices'])
            indices = indices.reshape((-1, 3))

            self._finalize_array_updates(indices, vertex_arrays)

        self._dirty_attributes.clear()

    def render_generic(self, *args, **kwargs):
        try:
            outline = self.outline.copy()
            translation = self.translation.copy()
            super(Polygons, self).render_generic(*args, **kwargs)
            if outline > 0:
                self.outline = -1
                self.translation = translation - (0, 0, 1e-3)
                super(Polygons, self).render_generic(*args, **kwargs)
        finally:
            self.outline = outline
            self.translation = translation
