import numpy as np
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Polygon

from ... import math
from ... import mesh
from ... import geometry
from ... import draw
from .internal import PatchUser

class ConvexPolyhedra(draw.ConvexPolyhedra, PatchUser):
    __doc__ = draw.ConvexPolyhedra.__doc__

    def _render_patches(self, axes, aa_pixel_size=0, rotation=(1, 0, 0, 0),
               ambient_light=0, directional_light=(-.1, -.25, -1), **kwargs):
        rotation = np.asarray(rotation)
        directional_light = np.atleast_2d(directional_light)
        collections = []

        (vertices, faces_) = geometry.convexHull(self.vertices)
        faces = [np.array(face, dtype=np.uint32) for face in faces_]

        (positions, orientations, shape_colors) = mesh.unfoldProperties([
            self.positions, self.orientations, self.colors])

        rotated_positions = math.quatrot(rotation[np.newaxis], positions)
        vertex_orientations = math.quatquat(
            orientations, rotation[np.newaxis])
        rotated_vertices = math.quatrot(
            vertex_orientations[:, np.newaxis], vertices[np.newaxis, :])
        rotated_vertices += rotated_positions[:, np.newaxis]

        outline = self.outline

        colors = []
        patches = []
        for (vertices, color) in zip(rotated_vertices, shape_colors):
            for face in faces:
                face_verts = vertices[face]
                z = np.min(face_verts[:, 2])
                normal = np.cross(face_verts[1] - face_verts[0],
                                  face_verts[-1] - face_verts[0])
                normal /= np.linalg.norm(normal)

                # cull back faces
                if normal[2] < 0:
                    continue

                if outline > 0:
                    outline_verts = face_verts
                    face_verts = geometry.insetPolygon(face_verts, outline)
                    outline_verts[:, :2] += np.sign(outline_verts[:, :2])*aa_pixel_size

                face_verts[:, :2] += np.sign(face_verts[:, :2])*aa_pixel_size

                light = ambient_light
                for light_direction in directional_light:
                    light += max(0, -np.dot(light_direction, normal))

                lit_color = color.copy()
                lit_color[:3] *= light

                patches.append(Polygon(face_verts[:, :2], closed=True, zorder=z))
                colors.append(lit_color)

                if outline > 0:
                    commands = ([Path.MOVETO] +
                                (face_verts.shape[0] - 1)*[Path.LINETO] +
                                [Path.CLOSEPOLY])
                    commands = 2*commands

                    # reverse the inner vertices order to make an open
                    # polygon. Duplicate the first vertex of each polygon to
                    # close the shapes.
                    outline_vertices = np.concatenate(
                        [outline_verts, outline_verts[:1],
                         face_verts[::-1], face_verts[:1]], axis=0)[:, :2]

                    outline_path = Path(outline_vertices, commands)
                    patches.append(PathPatch(outline_path, zorder=z))
                    colors.append(lit_color*(0, 0, 0, 1))

        colors = np.clip(colors, 0, 1)
        return [(patches, colors)]
