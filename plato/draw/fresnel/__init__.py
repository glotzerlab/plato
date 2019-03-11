"""
The fresnel backend uses `fresnel <https://github.com/glotzerlab/fresnel>`_
to ray-trace scenes.

All fresnel primitives accept an argument ``material`` of type :py:class:`fresnel.material.Material` to define how lights interact with the primitives.

.. note::

  Translucency is not currently supported in the fresnel backend. All
  particles will be opaque.

"""

from .Scene import Scene

from .Arrows2D import Arrows2D
from .Disks import Disks
from .Polygons import Polygons
from .Spheropolygons import Spheropolygons
from .Lines import Lines
from .Spheres import Spheres
from .SphereUnions import SphereUnions
from .ConvexPolyhedra import ConvexPolyhedra
