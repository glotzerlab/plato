import numpy as np
from ... import math
from ... import geometry
from ... import draw
from matplotlib.collections import PatchCollection
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Polygon
from matplotlib.transforms import Affine2D

class ConvexPolyhedra(draw.ConvexPolyhedra):
    __doc__ = draw.ConvexPolyhedra.__doc__

    def render(self, axes, aa_pixel_size=0, rotation=(1, 0, 0, 0),
               ambient_light=0, directional_light=(-.1, -.25, -1), **kwargs):
        rotation = np.asarray(rotation)
        directional_light = np.atleast_2d(directional_light)
        collections = []

        (vertices, faces_) = geometry.convexHull(self.vertices)
        faces = [np.array(face, dtype=np.uint32) for face in faces_]

        rotated_positions = math.quatrot(rotation[np.newaxis], self.positions)
        vertex_orientations = math.quatquat(
            self.orientations, rotation[np.newaxis])
        rotated_vertices = math.quatrot(
            vertex_orientations[:, np.newaxis], vertices[np.newaxis, :])
        rotated_vertices += rotated_positions[:, np.newaxis]

        colors = []
        patches = []
        for (vertices, color) in zip(rotated_vertices, self.colors):
            for face in faces:
                face_verts = vertices[face]
                z = np.min(face_verts[:, 2])
                normal = np.cross(face_verts[1] - face_verts[0],
                                  face_verts[-1] - face_verts[0])
                normal /= np.linalg.norm(normal)

                # cull back faces
                if normal[2] < 0:
                    continue

                light = ambient_light
                for light_direction in directional_light:
                    light += -np.dot(light_direction, normal)
                light = max(0, light)

                lit_color = color.copy()
                lit_color[:3] *= light

                face_verts[:, :2] += np.sign(face_verts[:, :2])*aa_pixel_size

                patches.append(Polygon(face_verts[:, :2], closed=True, zorder=-z))
                colors.append(lit_color)
        patches = PatchCollection(patches)
        patches.set_facecolor(np.clip(colors, 0, 1))
        collections.append(patches)

        for collection in collections:
            axes.add_collection(collection)
