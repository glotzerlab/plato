"""
The zdog backend uses `zdog <https://zzz.dog>`_ to render
shapes. Zdog is an HTML canvas-based engine that works best for
simple, cartoon-style illustrations. Plato's implementation works inside
notebook environments and also supports rendering standalone HTML for
inclusion in other pages.
"""

from .Scene import Scene

from .Arrows2D import Arrows2D
from .Box import Box
from .ConvexPolyhedra import ConvexPolyhedra
from .ConvexSpheropolyhedra import ConvexSpheropolyhedra
from .Disks import Disks
from .Lines import Lines
from .Polygons import Polygons
from .Spheres import Spheres
from .Spheropolygons import Spheropolygons
