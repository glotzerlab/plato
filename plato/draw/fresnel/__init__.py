"""
The fresnel backend uses `fresnel <https://bitbucket.org/glotzer/fresnel>`_
to ray-trace scenes.

All fresnel primitives accept an argument ``material`` of type :py:class:`fresnel.material.Material` to define how lights interact with the primitives.
"""

from .Scene import Scene

#from .Arrows2D import Arrows2D  # not working yet
from .Disks import Disks
from .Polygons import Polygons
from .Lines import Lines
from .Spheres import Spheres
from .ConvexPolyhedra import ConvexPolyhedra
