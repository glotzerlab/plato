import numpy as np
import rowan
from ... import mesh as pmesh
from ... import geometry

class PolyhedronRenderer:
    def render(self, rotation=(1, 0, 0, 0), name_suffix='', illo_id='illo',
               ambient_light=0.4, directional_light=[], stroke=False,
               outline=False, **kwargs):

        # in the zdog coordinate system, x is to the right, y is down,
        # and z is toward you
        lines = []

        stroke = stroke or 'false'

        (vertices, faces) = geometry.convexHull(self.vertices)

        face_normals = []
        face_paths = []
        for face in faces:
            r01 = vertices[face[1]] - vertices[face[0]]
            r12 = vertices[face[2]] - vertices[face[1]]
            normal = np.cross(r01, r12)
            normal /= np.linalg.norm(normal)
            face_normals.append(normal)

            path = ', '.join('{{x: {}, y: {}, z: {}}}'.format(*v) for v in vertices[face]*(1, -1, 1))
            face_paths.append(path)
        face_normals = np.array(face_normals, dtype=np.float32)

        orientations_euler = rowan.to_euler(
            self.orientations, convention='xyz', axis_type='intrinsic')

        particles = zip(
            self.positions*(1, -1, 1), self.orientations,
            -orientations_euler, self.colors*255)
        for i, (position, orientation, eulers, color) in enumerate(particles):
            group_index = 'convexPoly_{}_{}'.format(name_suffix, i)

            # full rotation to apply to vectors from base orientation
            # to final scene orientation
            full_rotation = rowan.multiply(rotation, orientation)

            lines.append("""
            let {group_index} = new Zdog.Group({{
                addTo: {illo_id},
                rotate: {{x: {angle[0]}, y: {angle[1]}, z: {angle[2]}}},
                translate: {{x: {pos[0]}, y: {pos[1]}, z: {pos[2]}}},
                updateSort: true,
            }});""".format(
                group_index=group_index, illo_id=illo_id, angle=eulers,
                pos=position))

            for (face_path, normal) in zip(face_paths, face_normals):
                rotated_normal = rowan.rotate(full_rotation, normal)

                light = ambient_light
                for direction in directional_light:
                    light += max(0, -np.dot(rotated_normal, direction))
                light = np.clip(light, 0, 1)

                (r, g, b) = map(int, light*color[:3])

                # RGB components are 0-255, A component is a float 0-1
                face_color = '"rgba({}, {}, {}, {})"'.format(r, g, b, color[3]/255)

                lines.append("""
                new Zdog.Shape({{
                    addTo: {group_index},
                    color: {face_color},
                    path: [{path}],
                    fill: true,
                    backface: true,
                    stroke: {stroke},
                }});
                """.format(
                    group_index=group_index, face_color=face_color, path=face_path,
                    stroke=stroke))

                if outline:
                    outline_color = '"rgba(0, 0, 0, {})"'.format(color[3]/255)
                    lines.append("""
                    new Zdog.Shape({{
                        addTo: {group_index},
                        color: {color},
                        path: [{path}],
                        fill: false,
                        stroke: {stroke},
                    }});
                    """.format(
                        group_index=group_index, color=outline_color, path=face_path,
                        stroke=outline))

        return lines
