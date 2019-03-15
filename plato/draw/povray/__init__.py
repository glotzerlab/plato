"""
The povray backend generates high-quality, ray-traced snapshots of
scenes by externally calling a povray binary. To use this backend,
povray should be installed and accessible on your executable path.
"""

from .Scene import Scene

from .Box import Box
from .ConvexPolyhedra import ConvexPolyhedra
from .ConvexSpheropolyhedra import ConvexSpheropolyhedra
from .Ellipsoids import Ellipsoids
from .Lines import Lines
from .Mesh import Mesh
from .Spheres import Spheres
from .SphereUnions import SphereUnions
