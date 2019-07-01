"""
The vispy backend uses `vispy <http://vispy.org/>`_ to render
shapes interactively using openGL. It supports both desktop use with a
variety of GUI backends and use inline in jupyter notebooks. While the
GUI backends are essentially interchangeable, the notebook backend is
more restrictive in its capabilities and some features are not
currently available with it.

Select the **vispy** backend to use with the standard vispy mechanism before
calling `Scene.show()`::

  import vispy, vispy.app
  # use in ipython notebook
  vispy.app.use_app('ipynb_webgl')
  # use pyside2
  vispy.app.use_app('pyside2')
  scene = plato.draw.vispy.Scene(...)
  scene.show()
  vispy.app.run()

"""

from .Scene import Scene

from .Arrows2D import Arrows2D
from .Disks import Disks
from .DiskUnions import DiskUnions
from .Ellipsoids import Ellipsoids
from .Polygons import Polygons
from .Spheropolygons import Spheropolygons
from .Voronoi import Voronoi
from .Lines import Lines
from .Spheres import Spheres
from .SpherePoints import SpherePoints
from .SphereUnions import SphereUnions
from .Mesh import Mesh
from .ConvexPolyhedra import ConvexPolyhedra
from .ConvexSpheropolyhedra import ConvexSpheropolyhedra
