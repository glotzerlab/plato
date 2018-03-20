import matplotlib, matplotlib.pyplot as pp
from ... import Scene
import numpy as np

class Scene(Scene):
    def show(self, figure=None, axes=None):
        if figure is None:
            figure = pp.figure()

        if axes is None:
            axes = figure.add_subplot(1, 1, 1)

        for prim in self._primitives:
            prim.render(figure, axes)

        (width, height) = self.size.astype(np.float32)/self.zoom
        axes.set_xticks([])
        axes.set_yticks([])
        axes.set_xlim(-width/2, width/2)
        axes.set_ylim(-height/2, height/2)
        axes.set_aspect(1)
        return figure
