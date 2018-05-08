import matplotlib, matplotlib.pyplot as pp
from ... import draw
import numpy as np

class Scene(draw.Scene):
    __doc__ = draw.Scene.__doc__ + """
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
            axes = figure.add_subplot(1, 1, 1)

        kwargs = dict(rotation=self.rotation,
                      size=self.size, pixel_scale=self.pixel_scale, zoom=self.zoom)

        if 'antialiasing' in self._enabled_features:
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

        for prim in self._primitives:
            prim.render(axes, **kwargs)

        (width, height) = self.size.astype(np.float32)/self.zoom
        (shift_x, shift_y, _) = -self.translation
        axes.axis('off')
        axes.set_xlim(-width/2 + shift_x, width/2 + shift_x)
        axes.set_ylim(-height/2 + shift_y, height/2 + shift_y)
        axes.set_aspect(1)
        return (figure, axes)

    def show(self, figure=None, axes=None):
        """Render and show the shapes in this Scene.

        :param figure: Figure object to render within (created using pyplot if not given)
        :param axes: Axes object to render within (created from the figure if not given)
        """
        (figure, _) = self.render(figure, axes)
        return figure.show()

    def save(self, filename):
        """Render and save an image of this Scene.

        :param filename: target filename to save the image into
        """
        (figure, _) = self.render()
        return figure.savefig(filename, dpi=figure.dpi)
