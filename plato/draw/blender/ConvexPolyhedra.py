import bpy
import itertools
from ... import geometry, math
from ... import draw
import numpy as np

class ConvexPolyhedra(draw.ConvexPolyhedra):

    def render(self, scene, suffix='', translation=(0, 0, 0),
               rotation=(1, 0, 0, 0)):
        rotation = np.asarray(rotation)
        prim_name = '{}_{}'.format(type(self).__name__, suffix)

        material = bpy.data.materials.new(prim_name)
        material.use_object_color = True

        (vertices, faces) = geometry.convexHull(self.vertices)
        mesh = bpy.data.meshes.new(prim_name)
        mesh.from_pydata(vertices, edges=[], faces=faces)
        mesh.materials.append(material)

        group = bpy.data.groups.new(prim_name)
        positions = math.quatrot(rotation[np.newaxis, :], self.positions)

        for (i, position, orientation, color) in zip(
                itertools.count(), positions, self.orientations, self.colors):
            shape_name = prim_name + '_{}'.format(i)
            shape = bpy.data.objects.new(shape_name, object_data=mesh)
            shape.location = position
            shape.rotation_mode = 'QUATERNION'
            shape.rotation_quaternion = orientation
            shape.color = color

            group.objects.link(shape)
            scene.objects.link(shape)
