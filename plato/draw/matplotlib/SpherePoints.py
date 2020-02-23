import numpy as np

from ... import draw
from ... import math

class SpherePoints(draw.SpherePoints):
    __doc__ = draw.SpherePoints.__doc__

    def render(self, axes, rotation=(1, 0, 0, 0), size=(2, 2), pixel_scale=64,
               zoom=1, **kwargs):
        rotation = np.asarray(rotation, dtype=np.float32)
        rotated_points = math.quatrot(self.rotation[np.newaxis], self.points)

        if self.on_surface:
            rotated_points /= np.linalg.norm(rotated_points, axis=-1, keepdims=True)
            rotated_points[np.isnan(rotated_points)] = 0

        size = np.asarray(size, dtype=np.float32)/zoom
        gridsize = int(np.max(np.asarray(size)*pixel_scale/self.blur*4))
        extent = (-size[0]/2, size[0]/2, -size[1]/2, size[1]/2)
        axes.hexbin(rotated_points[:, 0], rotated_points[:, 1], gridsize=gridsize,
                    extent=extent)
