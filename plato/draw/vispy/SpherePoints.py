import itertools

import numpy as np

from .internal import GLPrimitive, GLShapeDecorator
from ... import draw
from ..internal import ShapeAttribute

@GLShapeDecorator
class SpherePoints(draw.SpherePoints, GLPrimitive):
    __doc__ = draw.SpherePoints.__doc__

    shaders = {}

    shaders['vertex'] = """
        uniform mat4 camera;
        uniform vec4 rotation;
        uniform vec3 translation;
        uniform float radius;
        uniform int on_surface;
        uniform float blur;

        attribute vec3 points;
        attribute vec4 shape_id;

        varying vec3 v_point;
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
            vec3 vertexPos;
            if(on_surface != 0)
                vertexPos = radius*normalize(points);
            else
                vertexPos = points;
            v_point = rotate(vertexPos, rotation);
            vertexPos = v_point + translation;
            gl_Position = camera * vec4(vertexPos, 1.0);
            gl_PointSize = blur;
            v_shape_id = shape_id;
        }
       """

    # in the future, can use gl_PointCoord to scale intensity of
    # points from center for nicer appeareance
    shaders['fragment'] = """
        precision highp float;

        uniform float blur;
        uniform float intensity;
        uniform float inverse_size;
        uniform int draw_front;

        varying vec3 v_point;

        void main()
        {
            vec2 delta = gl_PointCoord - vec2(0.5, 0.5);
            float rsq = dot(delta, delta);
            float blursq = blur*blur;
            if(rsq > 0.25)
                discard;
            float prefactor = intensity*inverse_size;
            prefactor *= 1.0 - 4.0*rsq;
            prefactor /= 0.0625*blursq;
            vec3 color = prefactor*vec3(1.0, 1.0, 1.0);
            if(v_point.z < 0.0)
                color.xy *= 0.5;
            else
            {
                color.z *= 0.5;
                if(draw_front == 0) discard;
            }
            gl_FragColor = vec4(color.xyz, 1.0);
        }
       """

    shaders['fragment_pick'] = """
        uniform float blur;
        uniform int draw_front;
        uniform vec4 pick_prim_index;

        varying vec3 v_point;
        varying vec4 v_shape_id;

        void main()
        {
            vec2 delta = gl_PointCoord - vec2(0.5, 0.5);
            float rsq = dot(delta, delta);
            if(rsq > 0.25)
                discard;

            if(v_point.z < 0.0)
            {
            }
            else if(draw_front == 0)
                discard;

            gl_FragColor = pick_prim_index + v_shape_id;
        }
       """

    _vertex_attribute_names = ['shape_id', 'points']

    _GL_UNIFORMS = list(itertools.starmap(ShapeAttribute, [
        ('camera', np.float32, np.eye(4), 2, False,
         'Internal: 4x4 Camera matrix for world projection'),
        ('rotation', np.float32, (1, 0, 0, 0), 1, False,
         'Internal: Rotation to be applied to each scene as a quaternion'),
        ('translation', np.float32, (0, 0, 0), 1, False,
         'Internal: Translation to be applied to the scene'),
        draw.SpherePoints._ATTRIBUTES_BY_NAME['blur'],
        draw.SpherePoints._ATTRIBUTES_BY_NAME['intensity'],
        draw.SpherePoints._ATTRIBUTES_BY_NAME['on_surface'],
        ('radius', np.float32, 1, 0, False,
         'Radius of the sphere to normalize to'),
        ('draw_front', np.uint32, 1, 0, False,
         'If True, draw only the points facing the viewer'),
        ('inverse_size', np.float32, 1, 0, False,
         'Internal: inverse size of the given points array')
        ]))

    def __init__(self, *args, **kwargs):
        GLPrimitive.__init__(self)
        draw.SpherePoints.__init__(self, *args, **kwargs)

    def update_arrays(self):
        try:
            for name in self._dirty_attributes:
                self._gl_vertex_arrays[name][:] = self._attributes[name]
                self._dirty_vertex_attribs.add(name)
        except (ValueError, KeyError):
            shape_ids = np.arange(len(self), dtype=np.uint32).view(np.uint8).reshape((-1, 4))
            shape_ids = shape_ids.astype(np.float32)/255

            self._gl_vertex_arrays['points'] = self.points
            self._gl_vertex_arrays['shape_id'] = shape_ids
            self._dirty_vertex_attribs.add('points')
            self._dirty_vertex_attribs.add('shape_id')

        self._dirty_attributes.clear()

    @property
    def points(self):
        return draw.SpherePoints.points.fget(self)

    @points.setter
    def points(self, value):
        draw.SpherePoints.points.fset(self, value)

        inverse_size = 1.0/max(1.0, self.points.shape[0])
        self.inverse_size = inverse_size

    def render_generic(self, programs, make_program_function, config={}):
        self.update_arrays()

        if len(programs) < 1:
            programs.append(make_program_function(config))
            self._dirty_vertex_attribs.update(self._gl_vertex_arrays)
            self._dirty_uniforms.update(self._gl_uniforms)

        for name in self._dirty_vertex_attribs:
            for program in itertools.chain(*self._all_program_sets):
                reshaped = self._gl_vertex_arrays[name]
                reshaped = reshaped.reshape((-1, reshaped.shape[-1]))
                program[name] = reshaped
        self._dirty_vertex_attribs.clear()

        for name in self._dirty_uniforms:
            for program in itertools.chain(*self._all_program_sets):
                program[name] = self._gl_uniforms[name]
        self._dirty_uniforms.clear()

        for program in programs:
            program.draw('points')
