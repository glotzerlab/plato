import functools
import itertools

import numpy as np
import vispy, vispy.app
from vispy import gloo

from ... import mesh
from ..internal import array_size_checkers, ATTRIBUTE_DOCSTRING_TEMPLATE
from ..Scene import DEFAULT_DIRECTIONAL_LIGHTS

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
        self._shader_substitutions = {}

        self._color_programs = []
        self._pick_programs = []
        self._plane_programs = []
        self._all_program_sets = [
            self._color_programs, self._pick_programs, self._plane_programs]

        self._webgl = 'webgl' in vispy.app.use_app().backend_name

        for attr in self._GL_UNIFORMS:
            size_checker = array_size_checkers[attr.dimension]
            value = size_checker(np.asarray(attr.default, dtype=attr.dtype))
            self._gl_uniforms[attr.name] = value

        for attr in self._GL_UNIFORMS:
            setattr(self, attr.name.replace('[]', ''), attr.default)

    def make_prelude(self, config={}):
        prelude_lines = []
        if self._webgl:
            prelude_lines.append('#define WEBGL')
        prelude = '\n'.join(prelude_lines) + '\n'
        return prelude

    def make_shader_substitutions(self, shader):
        for name in self._shader_substitutions:
            shader = shader.replace(name, self._shader_substitutions[name])
        return shader

    def make_color_program(self, config={}):
        prelude = self.make_prelude(config)
        vertex = self.make_shader_substitutions(prelude + self.shaders['vertex'])
        fragment = self.make_shader_substitutions(prelude + self.shaders['fragment'])
        return gloo.Program(vertex, fragment)

    def make_pick_program(self, config={}):
        prelude = self.make_prelude(config)
        vertex = self.make_shader_substitutions(prelude + self.shaders['vertex'])
        fragment = self.make_shader_substitutions(prelude + self.shaders['fragment_pick'])
        return gloo.Program(vertex, fragment)

    def make_plane_program(self, config={}):
        prelude = self.make_prelude(config)
        vertex = self.make_shader_substitutions(prelude + self.shaders['vertex'])
        fragment = self.make_shader_substitutions(prelude + self.shaders['fragment_plane'])
        return gloo.Program(vertex, fragment)

    def render_generic(self, programs, make_program_function, config={}):
        self.update_arrays()

        for _ in range(len(programs), len(self._gl_vertex_arrays['indices'])):
            try:
                programs.append(make_program_function(config))
            except KeyError:
                # we were missing some shader code
                continue
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
        self._dirty_vertex_attribs.clear()

        for name in self._dirty_uniforms:
            for program in itertools.chain(*self._all_program_sets):
                if name.endswith('[]'):
                    base_name = name[:-2]
                    for (index, val) in enumerate(self._gl_uniforms[name]):
                        target = '{}[{}]'.format(base_name, index)
                        program[target] = val
                elif name in program:
                    program[name] = self._gl_uniforms[name]

        self._dirty_uniforms.clear()

        for (program, (_, buf)) in zip(programs, self._gl_vertex_arrays['indices']):
            program.draw('triangles', indices=buf)

    def render_color(self):
        self.render_generic(self._color_programs, self.make_color_program)

    def render_planes(self):
        self._gl_uniforms['render_positions'] = 0
        self._dirty_uniforms.add('render_positions')
        self.render_generic(self._plane_programs, self.make_plane_program)

    def render_normals(self):
        self._gl_uniforms['render_positions'] = -1
        self._dirty_uniforms.add('render_positions')
        self.render_generic(self._plane_programs, self.make_plane_program)

    def render_pick(self, index=0):
        # skip rendering shapes that don't have a pick shader
        if 'fragment_pick' not in self.shaders:
            return

        index = np.array([index], dtype=np.uint32).view(np.uint8)
        index = index.astype(np.float32)/255
        self._gl_uniforms['pick_prim_index'] = index
        self._dirty_uniforms.add('pick_prim_index')
        self.render_generic(self._pick_programs, self.make_pick_program)

    def render_positions(self):
        self._gl_uniforms['render_positions'] = 1
        self._dirty_uniforms.add('render_positions')
        self.render_generic(self._plane_programs, self.make_plane_program)

    def render_translucency(self, pass_=0):
        try:
            self._gl_uniforms['transparency_mode'] = pass_
            self._dirty_uniforms.add('transparency_mode')
            self.render_generic(self._color_programs, self.make_color_program)
        finally:
            self._gl_uniforms['transparency_mode'] = 0
            self._dirty_uniforms.add('transparency_mode')

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
    try:
        self._attributes[name] = result
    except AttributeError:
        # only called on initialization, skip before plato.draw.Shape
        # constructor has been called
        pass
    if name.endswith('[]'):
        key = 'NUM_{}'.format(name[:-2].upper())
        value = str(result.shape[0])
        if self._shader_substitutions.get(key, None) != value:
            for pset in self._all_program_sets:
                pset.clear()
            self._shader_substitutions[key] = value

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

        setattr(cls, attr.name.replace('[]', ''), prop)

    doc = cls.__doc__ or ''

    if len(attribute_doc_lines) > 1:
        doc += '\n'.join(attribute_doc_lines)
        cls.__doc__ = doc
    return cls
