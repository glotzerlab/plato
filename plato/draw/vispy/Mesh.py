from collections import defaultdict
import itertools
import numpy as np
from ... import mesh
from .internal import GLPrimitive, GLShapeDecorator
from ... import prims
from ...prims.internal import ShapeAttribute
from vispy import gloo

@GLShapeDecorator
class Mesh(prims.Mesh, GLPrimitive):
    __doc__ = prims.Mesh.__doc__

    shaders = {}

    shaders['vertex'] = """
       uniform mat4 camera;
       uniform vec4 rotation;
       uniform vec3 translation;
       uniform vec3 diffuseLight;

       attribute vec4 color;
       attribute vec3 normal;
       attribute vec3 image;

       varying vec4 v_color;
       varying vec3 v_normal;
       varying float v_light;
       varying vec3 v_position;

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
           vertexPos = rotate(vertexPos, rotation) + translation;
           vec4 screenPosition = camera * vec4(vertexPos, 1.0);
           vec3 rotatedNormal = rotate(normal, rotation);

           // transform to screen coordinates
           gl_Position = screenPosition;
           v_color = color;
           v_normal = rotatedNormal;
           v_light = -dot(rotatedNormal, diffuseLight);
           v_position = vertexPos;
       }
       """

    shaders['fragment'] = """
       varying vec4 v_color;
       varying vec3 v_normal;
       varying vec3 v_position;
       varying float v_light;

       // base light level
       uniform float ambientLight;
       // (x, y, z) direction*intensity
       uniform vec3 diffuseLight;
       uniform float u_pass;
       uniform float light_levels;

       void main()
       {
           float light = max(0.0, v_light);
           light += ambientLight;

           if(light_levels > 0.0)
           {
               light *= light_levels;
               light = floor(light);
               light /= light_levels;
           }

           #ifdef IS_TRANSPARENT
           float z = abs(v_position.z);
           float alpha = v_color.a;
           //float weight = pow(alpha, 1.0f) * clamp(0.002f/(1e-5f + pow(z/200.0f, 4.0f)), 1e-2, 3e3);
           float weight = alpha * max(3.0*pow(10.0, 3.0)*pow((1-(gl_FragCoord.z)), 3.0f), 1e-2);

           if( u_pass < 0.5 )
           {
              gl_FragColor = vec4(v_color.rgb * alpha * light, alpha) * weight;
           }
           else
           {
              gl_FragColor = vec4(alpha);
           }
           #else
           gl_FragColor = vec4(v_color.xyz*light, v_color.w);
           #endif
       }
       """

    shaders['fragment_plane'] = """
       varying vec4 v_color;
       varying vec3 v_normal;
       varying vec3 v_position;

       uniform mat4 camera;
       // base light level
       uniform float ambientLight;
       // (x, y, z) direction*intensity
       uniform vec3 diffuseLight;
       uniform float renderPositions = 0.0;

       void main()
       {
           if(renderPositions > 0.5)
               gl_FragColor = vec4(gl_FragCoord.xyz, 1.0);
           else // Store the plane equation as a color
               gl_FragColor = vec4(v_normal, dot(v_normal, v_position.xyz));
       }
       """

    _vertex_attribute_names = ['color', 'normal', 'image']

    _GL_UNIFORMS = list(itertools.starmap(ShapeAttribute, [
        ('camera', np.float32, np.eye(4), 2,
         '4x4 Camera matrix for world projection'),
        ('ambientLight', np.float32, .25, 0,
         'Ambient (minimum) light level for all surfaces'),
        ('diffuseLight', np.float32, (.5, .5, .5), 1,
         'Diffuse light direction*magnitude'),
        ('rotation', np.float32, (1, 0, 0, 0), 1,
         'Rotation to be applied to each scene as a quaternion'),
        ('translation', np.float32, (0, 0, 0), 1,
         'Translation to be applied to the scene'),
        ('light_levels', np.float32, 0, 0,
         'Number of light levels to quantize to (0: disable)')
        ]))

    def __init__(self, *args, **kwargs):
        GLPrimitive.__init__(self)
        prims.Mesh.__init__(self, *args, **kwargs)

    def update_arrays(self):
        if 'vertices' in self._dirty_attributes:
            image = self.vertices
            indices = self.indices

            # compute the vertex normals
            # first, compute the normal for each face
            expandedVertices = image[indices]
            faceNormals = np.cross(expandedVertices[:, 1, :] - expandedVertices[:, 0, :],
                                    expandedVertices[:, 2, :] - expandedVertices[:, 0, :])
            faceNormals /= np.linalg.norm(faceNormals, axis=-1, keepdims=True)

            # store the normals of faces adjacent to each vertex here
            vertexFaceNormals = defaultdict(list)

            for ((i, j, k), normal) in zip(indices, faceNormals):
                vertexFaceNormals[i].append(normal)
                vertexFaceNormals[j].append(normal)
                vertexFaceNormals[k].append(normal)

            # use the (normalized) mean normal of each adjacent face
            # as the vertex normal
            vertexNormals = []
            for i in range(len(image)):
                if vertexFaceNormals[i]:
                    normal = np.mean(vertexFaceNormals[i], axis=0)
                    normal /= np.linalg.norm(normal)
                else:
                    normal = [0, 0, 0]
                vertexNormals.append(normal)

            normal = np.array(vertexNormals, dtype=np.float32)

            self._gl_attributes['image'] = self.vertices
            self._gl_attributes['normal'] = normal
            self._gl_attributes['indices'] = indices

        try:
            for name in self._dirty_attributes:
                self._gl_vertex_arrays[name][:] = self._attributes[name]
                self._dirty_vertex_attribs.add(name)
        except (ValueError, KeyError):
            vertex_arrays = [self.colors] + [self._gl_attributes[name] for name in ['normal', 'image']]
            indices = self._gl_attributes['indices'].reshape((-1, 3))

            self._finalize_array_updates(indices, vertex_arrays)

        self._dirty_attributes.clear()
