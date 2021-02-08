"""
The fresnel backend uses `fresnel <https://github.com/glotzerlab/fresnel>`_
to generate high-quality, ray-traced images of scenes.

All fresnel primitives accept an argument ``material`` of type
:py:class:`fresnel.material.Material` to define how lights interact
with the primitives.

.. note::

  Translucency is not currently supported in the fresnel backend. All
  particles will be opaque.

"""

from .Scene import Scene

from .Arrows2D import Arrows2D
from .Box import Box
from .ConvexPolyhedra import ConvexPolyhedra
from .Disks import Disks
from .Ellipsoids import Ellipsoids
from .Lines import Lines
from .Mesh import Mesh
from .Polygons import Polygons
from .Spheres import Spheres
from .SphereUnions import SphereUnions
from .Spheropolygons import Spheropolygons
