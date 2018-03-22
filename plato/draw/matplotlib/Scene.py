import matplotlib, matplotlib.pyplot as pp
from .. import Scene
import numpy as np

class Scene(Scene):
    def render(self, figure=None, axes=None):
        if figure is None:
            figure = pp.figure()

        if axes is None:
            axes = figure.add_subplot(1, 1, 1)

        if 'antialiasing' in self._enabled_features:
            pixel_size = np.array(figure.get_size_inches(), dtype=np.float32)*figure.dpi
            antialiasing_pixel_size = np.max(np.array(self.size, dtype=np.float32)/pixel_size)/self.zoom
        else:
            antialiasing_pixel_size = 0

        for prim in self._primitives:
            prim.render(axes, antialiasing_pixel_size)

        (width, height) = self.size.astype(np.float32)/self.zoom
        axes.set_xticks([])
        axes.set_yticks([])
        axes.set_xlim(-width/2, width/2)
        axes.set_ylim(-height/2, height/2)
        axes.set_aspect(1)
        return (figure, axes)

    def show(self, figure=None, axes=None):
        (figure, _) = self.render(figure, axes)
        return figure.show()

    def save(self, filename):
        (figure, _) = self.render()
        return figure.savefig(filename)
