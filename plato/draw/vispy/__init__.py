"""
The vispy backend uses `vispy <http://vispy.org/>`_ to render shapes
interactively using openGL. It supports both desktop use with a
variety of GUI backends and use inline in jupyter notebooks.
"""

from .Scene import Scene

from .Arrows2D import Arrows2D
from .Disks import Disks
from .Polygons import Polygons
from .Spheropolygons import Spheropolygons
from .Voronoi import Voronoi
from .Lines import Lines
from .Spheres import Spheres
from .SpherePoints import SpherePoints
from .Mesh import Mesh
from .ConvexPolyhedra import ConvexPolyhedra
from .ConvexSpheropolyhedra import ConvexSpheropolyhedra
