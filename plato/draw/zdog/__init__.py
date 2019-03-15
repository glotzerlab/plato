"""
The zdog backend uses `zdog <https://zzz.dog>`_ to render
shapes. Zdog is an HTML canvas-based engine that works best for
simple, cartoon-style illustrations. Plato's implementation works inside
notebook environments and also supports rendering standalone HTML for
inclusion in other pages.
"""

from .Scene import Scene

from .Box import Box
from .ConvexPolyhedra import ConvexPolyhedra
from .ConvexSpheropolyhedra import ConvexSpheropolyhedra
from .Lines import Lines
from .Spheres import Spheres
