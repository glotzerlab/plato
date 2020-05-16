import numpy as np
import rowan

from ... import draw, mesh

class Ellipsoids(draw.Ellipsoids):
    __doc__ = draw.Ellipsoids.__doc__

    def render(self, rotation=(1, 0, 0, 0), translation=(0, 0, 0), **kwargs):
        (positions, orientations, colors) = mesh.unfoldProperties([
            self.positions, self.orientations, self.colors])
        positions = rowan.rotate(rotation, positions)
        positions += translation
        orientations = rowan.multiply(
            rotation, rowan.normalize(orientations))
        rotations = np.degrees(rowan.to_euler(orientations))

        lines = []
        for (pos, rot, col, alpha) in zip(
                positions, rotations, colors[:, :3], 1 - colors[:, 3]):
            lines.append('sphere {{ '
                         '0, 1 scale<{a}, {b}, {c}> '
                         'rotate <{rot[2]}, {rot[1]}, {rot[0]}> '
                         'translate <{pos[0]}, {pos[1]}, {pos[2]}> '
                         'pigment {{ color <{col[0]}, {col[1]}, {col[2]}> transmit {alpha} }} '
                         '}}'.format(a=self.a, b=self.b, c=self.c,
                                     pos=pos, rot=rot, col=col, alpha=alpha))
        return lines
