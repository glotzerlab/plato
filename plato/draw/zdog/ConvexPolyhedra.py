from ... import draw
from .internal import PolyhedronRenderer

class ConvexPolyhedra(draw.ConvexPolyhedra, PolyhedronRenderer):
    __doc__ = draw.ConvexPolyhedra.__doc__

    def render(self, *args, **kwargs):
        if self.outline:
            kwargs['outline'] = self.outline
        kwargs['stroke'] = False
        return PolyhedronRenderer.render(self, *args, **kwargs)
