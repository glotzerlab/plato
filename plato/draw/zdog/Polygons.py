from ... import draw
from .internal import PolygonRenderer

class Polygons(draw.Polygons, PolygonRenderer):
    __doc__ = draw.Polygons.__doc__

    def render(self, *args, **kwargs):
        if self.outline:
            kwargs['outline'] = self.outline
        kwargs['stroke'] = False
        return PolygonRenderer.render(self, *args, **kwargs)
