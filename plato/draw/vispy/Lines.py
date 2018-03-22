import itertools
import numpy as np
from ... import mesh
from .internal import GLPrimitive, GLShapeDecorator
from ... import draw
from ..internal import ShapeAttribute
from vispy import gloo

@GLShapeDecorator
class Lines(draw.Lines, GLPrimitive):
    __doc__ = draw.Lines.__doc__

    shaders = {}

    shaders['vertex'] = """
       uniform mat4 camera;
       uniform vec4 rotation;
       uniform vec3 translation;

       attribute vec4 color;
       attribute vec3 start_point;
       attribute vec3 end_point;
       attribute vec2 image;
       attribute float width;

       varying vec4 v_color;
       varying float v_depth;

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
           vec3 startPos = rotate(start_point, rotation) + translation;
           vec3 endPos = rotate(end_point, rotation) + translation;

           vec3 vertexPos = (startPos + endPos)/2.0;
           vertexPos = rotate(vertexPos, rotation) + translation;

           vec4 startScreenPosition = camera * vec4(startPos, 1.0);
           vec4 endScreenPosition = camera * vec4(endPos, 1.0);

           vec4 screenPosition = (1.0 - image.y)*startScreenPosition + image.y*endScreenPosition;

           vec2 realDisplacement = vec2(endScreenPosition.x - startScreenPosition.x, endScreenPosition.y - startScreenPosition.y);
           vec2 normDisplacement = normalize(realDisplacement);
           vec2 delta = vec2(normDisplacement.y, -normDisplacement.x)*width*image.x;

           delta.x *= camera[0][0];
           delta.y *= camera[1][1];

           gl_Position = vec4(screenPosition.xy + delta, screenPosition.z, screenPosition.w);
           v_color = color;
           v_depth = vertexPos.z;
       }

    """

    shaders['fragment'] = """

       varying vec4 v_color;
       varying float v_depth;
       uniform float u_pass;

       void main()
       {
           #ifdef IS_TRANSPARENT
           float z = abs(v_depth);
           float alpha = v_color.a;
           float weight = alpha * max(3.0*pow(10.0, 3.0)*pow((1-(gl_FragCoord.z)), 3.0f), 1e-2);

           if( u_pass < 0.5 )
           {
              gl_FragColor = vec4(v_color.rgb *alpha, alpha) * weight;
           }
           else
           {
              gl_FragColor = vec4(alpha);
           }
           #else
           gl_FragColor = vec4(v_color.xyz, v_color.w);
           #endif
       }
       """

    _vertex_attribute_names = ['start_point', 'end_point', 'color', 'width', 'image']

    _GL_UNIFORMS = list(itertools.starmap(ShapeAttribute, [
        ('camera', np.float32, np.eye(4), 2,
         '4x4 Camera matrix for world projection'),
        ('rotation', np.float32, (1, 0, 0, 0), 1,
         'Rotation to be applied to each scene as a quaternion'),
        ('translation', np.float32, (0, 0, 0), 1,
         'Translation to be applied to the scene')
        ]))

    def __init__(self, *args, **kwargs):
        GLPrimitive.__init__(self)
        draw.Lines.__init__(self, *args, **kwargs)

    def update_arrays(self):
        try:
            for name in self._dirty_attributes:
                self._gl_vertex_arrays[name][:] = self._attributes[name]
                self._dirty_vertex_attribs.add(name)
        except (ValueError, KeyError):
            # vertices for a unit square
            # This square will be transformed in order for us to draw our line
            square = np.array([[-1/2, 0],
                                 [1/2, 0],
                                 [1/2, 1.0],
                                 [-1/2, 1.0]], dtype=np.float32)

            vertex_arrays = mesh.unfoldProperties(
                [self.start_points, self.end_points, self.colors, self.widths],
                [square])

            unfolded_shape = vertex_arrays[0].shape[:-1]
            indices = (np.arange(unfolded_shape[0])[:, np.newaxis, np.newaxis]*unfolded_shape[1] +
                       np.array([[0, 1, 2], [2, 3, 0]], dtype=np.uint32))
            indices = indices.reshape((-1, 3))

            self._finalize_array_updates(indices, vertex_arrays)

        self._dirty_attributes.clear()

    def render_planes(self):
        # Not currently supported, but we shouldn't error out in the middle of rendering
        pass

    def render_positions(self):
        # Not currently supported, but we shouldn't error out in the middle of rendering
        pass
