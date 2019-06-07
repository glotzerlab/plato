"""
The matplotlib backend uses matplotlib to render shapes. Different
matplotlib backends can be configured for interactivity, but plato
does not currently otherwise support interactive manipulation of
shapes using this backend.
"""

from .Arrows2D import Arrows2D
from .ConvexPolyhedra import ConvexPolyhedra
from .Disks import Disks
from .DiskUnions import DiskUnions
from .Polygons import Polygons
from .Scene import Scene
from .SpherePoints import SpherePoints
from .Spheres import Spheres
from .Spheropolygons import Spheropolygons
from .Voronoi import Voronoi
