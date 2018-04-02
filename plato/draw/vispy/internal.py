import functools
import itertools
import numpy as np
import vispy, vispy.app
from vispy import gloo
from ... import mesh
from ..internal import array_size_checkers, ATTRIBUTE_DOCSTRING_TEMPLATE

ATTRIBUTE_DOCSTRING_HEADER = '\n\nThis primitive has the following opengl-specific attributes:'

class GLPrimitive:
    def __init__(self):
        # hold intermediate computations wrt convex hull/meshes
        self._gl_attributes = {}

        # hold unfolded vertex attrib arrays
        self._gl_vertex_arrays = {}
        self._dirty_vertex_attribs = set()
        self._gl_uniforms = {}
        self._dirty_uniforms = set()

        self._color_programs = []
        self._plane_programs = []
        self._all_program_sets = [self._color_programs, self._plane_programs]

        self._webgl = 'webgl' in vispy.app.use_app().backend_name

        for attr in self._GL_UNIFORMS:
            size_checker = array_size_checkers[attr.dimension]
            value = size_checker(np.asarray(attr.default, dtype=attr.dtype))
            self._gl_uniforms[attr.name] = value

    def make_prelude(self, config={}):
        prelude_lines = []
        if self._webgl:
            prelude_lines.append('#define WEBGL')
        prelude = '\n'.join(prelude_lines) + '\n'
        return prelude

    def make_color_program(self, config={}):
        prelude = self.make_prelude(config)
        return gloo.Program(prelude + self.shaders['vertex'], prelude + self.shaders['fragment'])

    def make_plane_program(self, config={}):
        prelude = self.make_prelude(config)
        return gloo.Program(prelude + self.shaders['vertex'], prelude + self.shaders['fragment_plane'])

    def render_generic(self, programs, make_program_function, config={}):
        self.update_arrays()

        for _ in range(len(programs), len(self._gl_vertex_arrays['indices'])):
            programs.append(make_program_function(config))
            self._dirty_vertex_attribs.update(self._gl_vertex_arrays)
            self._dirty_uniforms.update(self._gl_uniforms)

        for name in self._dirty_vertex_attribs:
            if name == 'indices':
                continue

            for program_set in self._all_program_sets:
                for (program, (scat, _)) in zip(
                        program_set, self._gl_vertex_arrays['indices']):
                    reshaped = self._gl_vertex_arrays[name]
                    reshaped = reshaped.reshape((-1, reshaped.shape[-1]))
                    program[name] = reshaped[scat]

        for name in self._dirty_uniforms:
            for program in itertools.chain(*self._all_program_sets):
                program[name] = self._gl_uniforms[name]

        for (program, (_, buf)) in zip(programs, self._gl_vertex_arrays['indices']):
            program.draw('triangles', indices=buf)

    def render_color(self):
        self.render_generic(self._color_programs, self.make_color_program)

    def render_planes(self):
        self._gl_uniforms['render_positions'] = 0
        self._dirty_uniforms.add('render_positions')
        self.render_generic(self._plane_programs, self.make_plane_program)

    def render_positions(self):
        self._gl_uniforms['render_positions'] = 1
        self._dirty_uniforms.add('render_positions')
        self.render_generic(self._plane_programs, self.make_plane_program)

    def _finalize_array_updates(self, indices, vertex_arrays):
        indexDtype = np.uint16 if self._webgl else np.uint32
        maxIndex = 2**16 - 1 if self._webgl else 2**32 - 1
        self._gl_vertex_arrays['indices'] = [(scat, gloo.IndexBuffer(np.ascontiguousarray(ind, dtype=indexDtype)))
            for (scat, ind) in mesh.splitChunks(indices, maxIndex=maxIndex)]

        for (name, value) in zip(self._vertex_attribute_names, vertex_arrays):
            self._gl_vertex_arrays[name] = value
            self._dirty_vertex_attribs.add(name)

def gl_uniform_setter(self, value, name, dtype, dimension, default):
    size_checker = array_size_checkers[dimension]
    result = size_checker(np.asarray(value, dtype=dtype))
    assert result.shape[-1:] == self._UNIFORM_DIMENSIONS[name], 'Invalid shape for uniform {}: {}'.format(name, result.shape)
    self._dirty_uniforms.add(name)
    self._gl_uniforms[name] = result

def gl_uniform_getter(self, name):
    return self._gl_uniforms[name]

def GLShapeDecorator(cls):
    cls._UNIFORM_DIMENSIONS = {}
    attribute_doc_lines = [ATTRIBUTE_DOCSTRING_HEADER]

    for attr in cls._GL_UNIFORMS:
        array_default = array_size_checkers[attr.dimension](attr.default)
        cls._UNIFORM_DIMENSIONS[attr.name] = array_default.shape[-1:]

        if not attr.description.lower().startswith('internal'):
            attribute_doc_lines.append(ATTRIBUTE_DOCSTRING_TEMPLATE.format(
                name=attr.name, description=attr.description))

        getter = functools.partial(gl_uniform_getter, name=attr.name)
        setter = functools.partial(
            gl_uniform_setter, name=attr.name, dtype=attr.dtype,
            dimension=attr.dimension, default=attr.default)
        prop = property(getter, setter, doc=attr.description)

        setattr(cls, attr.name, prop)

    if cls.__doc__ is None:
        cls.__doc__ = ''

    if len(attribute_doc_lines) > 1:
        cls.__doc__ += '\n'.join(attribute_doc_lines)
    return cls
