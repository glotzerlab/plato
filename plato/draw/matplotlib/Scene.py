import contextlib

import matplotlib.pyplot as pp
from matplotlib.collections import PatchCollection
import numpy as np

from ... import draw

@contextlib.contextmanager
def manage_matplotlib_interactive():
    was_interactive = pp.isinteractive()
    pp.ioff()

    yield None
    if was_interactive:
        pp.ion()

class Scene(draw.Scene):
    __doc__ = (draw.Scene.__doc__ or '') + """
    This Scene supports the following features:

    * *antialiasing*: Enable antialiasing. Primitives that support antialiasing will fudge some distances (typically for drawing outlines) to reduce visual artifacts.
    """

    def render(self, figure=None, axes=None):
        """Render all the shapes in this Scene.

        :param figure: Figure object to render within (created using pyplot if not given)
        :param axes: Axes object to render within (created from the figure if not given)
        """
        if figure is None:
            dpi = pp.rcParams.get('figure.dpi', 72)
            real_size = self.size_pixels/dpi
            figure = pp.figure(figsize=real_size, dpi=dpi)

        if axes is None:
            axes = figure.add_axes([0, 0, 1, 1], frame_on=False, xmargin=0, ymargin=0)

        kwargs = dict(rotation=self.rotation,
                      size=self.size, pixel_scale=self.pixel_scale, zoom=self.zoom)

        if 'antialiasing' in self.enabled_features:
            pixel_size = np.array(figure.get_size_inches(), dtype=np.float32)*figure.dpi
            kwargs['aa_pixel_size'] = np.max(np.array(self.size, dtype=np.float32)/pixel_size)/self.zoom
        else:
            kwargs['aa_pixel_size'] = 0

        if 'ambient_light' in self.enabled_features:
            kwargs['ambient_light'] = self.get_feature_config('ambient_light')['value']

        feature_cfg = self.get_feature_config('directional_light')
        if feature_cfg is not None:
            lights = feature_cfg.get('value', (.25, .5, -1))
            lights = np.atleast_2d(lights).astype(np.float32)
            kwargs['directional_light'] = lights

        current_patches = []
        for prim in self._primitives:
            if hasattr(prim, '_render_patches'):
                current_patches.extend(prim._render_patches(axes, **kwargs))
            else:
                # render any patches that have accumulated
                self._render_patches(current_patches, axes)
                prim.render(axes, **kwargs)
        self._render_patches(current_patches, axes)

        (width, height) = self.size.astype(np.float32)/self.zoom
        (shift_x, shift_y, _) = -self.translation
        axes.get_xaxis().set_visible(False)
        axes.get_yaxis().set_visible(False)
        axes.autoscale(False, tight=True)
        axes.set_xlim(-width/2 + shift_x, width/2 + shift_x)
        axes.set_ylim(-height/2 + shift_y, height/2 + shift_y)
        axes.set_aspect(1)
        return (figure, axes)

    def _render_patches(self, patches, axes):
        if not patches:
            return

        all_patches = []
        all_colors = []
        for (p, c) in patches:
            all_patches.extend(p)
            all_colors.append(c)

        all_colors = np.concatenate(all_colors, axis=0)

        sort_indices = np.argsort([patch.zorder for patch in all_patches])
        collection = PatchCollection([all_patches[i] for i in sort_indices])
        collection.set_facecolor(all_colors[sort_indices])
        axes.add_collection(collection)

        patches.clear()

    def show(self, figure=None, axes=None):
        """Render and show the shapes in this Scene.

        :param figure: Figure object to render within (created using pyplot if not given)
        :param axes: Axes object to render within (created from the figure if not given)
        """
        (figure, _) = self.render(figure, axes)
        return figure.show()

    def save(self, filename, figure=None, axes=None):
        """Render and save an image of this Scene.

        :param filename: target filename to save the image into
        """
        (figure, _) = self.render(figure, axes)
        return figure.savefig(filename, dpi=figure.dpi, bbox_inches='tight',
                              pad_inches=0)

    def _ipython_display_(self):
        import IPython.display
        with manage_matplotlib_interactive():
            (fig, _) = self.render()
        return IPython.display.display(fig, display_id=str(id(self)))
