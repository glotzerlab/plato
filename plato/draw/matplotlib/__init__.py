"""
The matplotlib backend uses matplotlib to render shapes. Different
matplotlib backends can be configured for interactivity, but plato
does not currently otherwise support interactive manipulation of
shapes using this backend.

Matplotlib has extensive support for a wide range of graphical
formats, so it is ideal for saving vector versions of figures.
"""

from .Scene import Scene

from .Arrows2D import Arrows2D
from .Box import Box
from .ConvexPolyhedra import ConvexPolyhedra
from .Disks import Disks
from .DiskUnions import DiskUnions
from .Lines import Lines
from .Polygons import Polygons
from .SpherePoints import SpherePoints
from .Spheres import Spheres
from .Spheropolygons import Spheropolygons
