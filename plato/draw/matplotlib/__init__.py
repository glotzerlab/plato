"""
The matplotlib backend uses matplotlib to render shapes. Different
matplotlib backends can be configured for interactivity, but plato
does not currently otherwise support interactive manipulation of
shapes using this backend.
"""

from .Scene import Scene

from .Disks import Disks
from .Polygons import Polygons
from .Spheropolygons import Spheropolygons

from .SpherePoints import SpherePoints
