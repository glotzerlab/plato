from ... import draw
from .Lines import Lines

class Box(draw.Box, Lines):
    __doc__ = draw.Box.__doc__

    def render(self, *args, **kwargs):
        Lines.render(self, *args, **kwargs)
