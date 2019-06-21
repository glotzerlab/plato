from ... import draw
from .internal import PolyhedronRenderer

class ConvexSpheropolyhedra(draw.ConvexSpheropolyhedra, PolyhedronRenderer):
    __doc__ = draw.ConvexSpheropolyhedra.__doc__

    def render(self, *args, **kwargs):
        kwargs['stroke'] = self.radius*2
        return PolyhedronRenderer.render(self, *args, **kwargs)
