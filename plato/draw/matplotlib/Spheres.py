import itertools
import numpy as np
from ... import math
from ... import geometry
from ... import draw
from ...draw import internal
from matplotlib.collections import PatchCollection
from matplotlib.path import Path
from matplotlib.patches import Circle

@internal.ShapeDecorator
class Spheres(draw.Spheres):
    __doc__ = draw.Spheres.__doc__

    _ATTRIBUTES = draw.Spheres._ATTRIBUTES + list(itertools.starmap(
        internal.ShapeAttribute, [
            ('light_levels', np.uint32, 3, 0,
             'Number of quantized light levels to use'),
        ]))

    def render(self, axes, aa_pixel_size=0, rotation=(1, 0, 0, 0),
               ambient_light=0, directional_light=(-.1, -.25, -1), **kwargs):
        rotation = np.asarray(rotation)
        directional_light = np.atleast_2d(directional_light)[0]
        light_magnitude = np.linalg.norm(directional_light)
        light_normal = directional_light/light_magnitude

        rotated_positions = math.quatrot(rotation[np.newaxis], self.positions)

        patches = []
        for level_fraction in np.linspace(1, 0, self.light_levels + 1, endpoint=False):
            # base values for radius=1
            offset = -light_normal*level_fraction

            these_colors = self.colors.copy()
            light_level = level_fraction*(1 - np.abs(light_normal[2])) + (1 - level_fraction)*1
            these_colors[:, :3] *= ambient_light + light_level*light_magnitude
            these_colors.clip(0, 1, these_colors)

            for (position, radius, color, index) in zip(
                    rotated_positions, self.radii, these_colors, itertools.count()):
                zorder = (position[2] - offset[2]*radius)
                patch = Circle(position[:2] + offset[:2]*radius,
                               radius*level_fraction, zorder=zorder,
                               color=color)

                # TODO fix clipping
                # if level_fraction < 1:
                #     patch.set_clip_path(patches[index])

                patches.append(patch)

        # matplotlib doesn't seem to support per-circle zorder for
        # circles in a PatchCollection, so add them directly to the
        # given axes object
        for patch in patches:
            axes.add_patch(patch)
