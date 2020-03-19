import itertools

from matplotlib.patches import Circle
import numpy as np

from ... import math
from ... import draw
from ... import mesh
from ...draw import internal
from .internal import PatchUser

@internal.ShapeDecorator
class Spheres(draw.Spheres, PatchUser):
    __doc__ = draw.Spheres.__doc__

    _ATTRIBUTES = draw.Spheres._ATTRIBUTES + list(itertools.starmap(
        internal.ShapeAttribute, [
            ('light_levels', np.uint32, 3, 0, False,
             'Number of quantized light levels to use'),
        ]))

    def _render_patches(self, axes, aa_pixel_size=0, rotation=(1, 0, 0, 0),
               ambient_light=0, directional_light=(-.1, -.25, -1), **kwargs):
        result = []
        colors = []

        rotation = np.asarray(rotation)
        directional_light = np.atleast_2d(directional_light)[0]
        light_magnitude = np.linalg.norm(directional_light)
        light_normal = directional_light/light_magnitude

        (positions, radii, shape_colors) = mesh.unfoldProperties([
            self.positions, self.radii, self.colors])

        rotated_positions = math.quatrot(rotation[np.newaxis], positions)

        patches = []
        for level_fraction in np.linspace(1, 0, self.light_levels + 1, endpoint=False):
            # base values for radius=1
            offset = -light_normal*level_fraction

            these_colors = shape_colors.copy()
            light_level = level_fraction*(1 - np.abs(light_normal[2])) + (1 - level_fraction)*1
            these_colors[:, :3] *= ambient_light + light_level*light_magnitude
            these_colors.clip(0, 1, these_colors)
            colors.append(these_colors)

            for (position, (radius,), color, index) in zip(
                    rotated_positions, radii, these_colors, itertools.count()):
                zorder = (position[2] - offset[2]*radius)
                patch = Circle(position[:2] + offset[:2]*radius,
                               radius*level_fraction, zorder=zorder,
                               color=color)

                # TODO fix clipping
                # if level_fraction < 1:
                #     patch.set_clip_path(patches[index])

                patches.append(patch)

        result.append((patches, np.concatenate(colors, axis=0)))

        return result
