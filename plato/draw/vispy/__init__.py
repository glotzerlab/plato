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

**Mouse controls:** Live vispy windows support rotating the scene in
three dimensions by dragging the mouse. Dragging while holding the
control or meta keys causes the mouse movement to rotate the scene
about the z axis and zoom in or out. Holding the alt key while
dragging the mouse cursor will translate the scene; for
two-dimensional scenes, it may be preferable to enable the `pan`
feature, which causes mouse motion to translate, rather than rotate,
the scene by default.

**Keyboard controls:** Live vispy windows also support controlling the
camera via the keyboard. Control or meta in conjunction with the arrow
keys rotate the system in 15 degree increments. The same functionality
is mapped to the I (up), J (left), K (down), and L (right) keys. X, Y,
and Z directly snap the scene to look down the x, y, or z axes,
respectively.
"""

import vispy
vispy.set_log_level('warning')

from .Scene import Scene

from .Box import Box
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
