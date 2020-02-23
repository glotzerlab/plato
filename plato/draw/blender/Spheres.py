import itertools

import bpy
import numpy as np

from ... import draw, math, mesh

class Spheres(draw.Spheres):

    def render(self, scene, suffix='', translation=(0, 0, 0),
               rotation=(1, 0, 0, 0)):
        rotation = np.asarray(rotation)
        prim_name = '{}_{}'.format(type(self).__name__, suffix)

        material = bpy.data.materials.new(prim_name)
        material.use_object_color = True

        shape_params = bpy.data.metaballs.new(prim_name)
        shape_params.materials.append(material)
        elt_params = shape_params.elements.new('BALL')

        group = bpy.data.groups.new(prim_name)
        positions = math.quatrot(rotation[np.newaxis, :], self.positions)

        particles = zip(*mesh.unfoldProperties([
            positions, self.radii, self.colors]))
        for (i, (position, (radius,), color)) in enumerate(particles):
            shape_name = prim_name + '_{}'.format(i)
            shape = bpy.data.objects.new(shape_name, object_data=shape_params)
            shape.location = position
            shape.color = color
            shape.scale = (radius, radius, radius)

            group.objects.link(shape)
            scene.objects.link(shape)
