"""
The `pythreejs <https://github.com/jupyter-widgets/pythreejs>`_
backend renders scenes using `three.js <https://threejs.org/>`_
and is compatible with Jupyter notebooks.

.. note::

    To enable translucency in the pythreejs backend, a primitive must have the
    same value of alpha (less than 1) for all colors.

"""

from .ConvexPolyhedra import ConvexPolyhedra
from .ConvexSpheropolyhedra import ConvexSpheropolyhedra
from .Ellipsoids import Ellipsoids
from .Lines import Lines
from .Mesh import Mesh
from .Spheres import Spheres
from .Scene import Scene
