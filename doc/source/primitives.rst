.. contents:: Plato primitives

================
Plato Primitives
================

Plato's graphics primitives all follow a fairly standard
form. Depending on the shapes to be rendered, different properties may
be per-particle (such as positions, orientations, and colors) or
global (the ConvexPolyhedra primitive is restricted to drawing any
number of identically-shaped convex polyhedra; in other words, the
vertices given are for all particles rendered).

Primitives' data can be set and retrieved through properties, which
are exposed as numpy arrays whenever possible. For example, to scale
the diameter of each disk in a Disks primitive by 2::

   disks = plato.draw.Disks(...)
   disks.diameters *= 2

Primitives can be grouped together by placing them in the same
:py:class:`plato.draw.Scene`.

The classes inside :py:mod:`plato.draw` are simple containers and are
not useful for visualization. Instead, a particular *backend* should
be used, for example::

  import plato.draw.matplotlib as draw
  disks = draw.Disks(...)
  scene = draw.Scene(disks, ...)
  scene.show()

Base Graphics Primitives
========================

.. py:module:: plato.draw

2D Graphics Primitives
----------------------

.. autoclass:: Disks
   :members:

.. autoclass:: Polygons
   :members:

.. autoclass:: Spheropolygons
   :members:

.. autoclass:: Arrows2D
   :members:

.. autoclass:: Voronoi
   :members:

3D Graphics Primitives
----------------------

.. autoclass:: Spheres
   :members:

.. autoclass:: Lines
   :members:

.. autoclass:: Mesh
   :members:

.. autoclass:: ConvexPolyhedra
   :members:

.. autoclass:: ConvexSpheropolyhedra
   :members:

.. autoclass:: SpherePoints
   :members:

Vispy Backend
=============

.. automodule:: plato.draw.vispy

2D Graphics Primitives
----------------------

.. autoclass:: Disks
   :members:

.. autoclass:: Polygons
   :members:

.. autoclass:: Spheropolygons
   :members:

.. autoclass:: Arrows2D
   :members:

.. autoclass:: Voronoi
   :members:

3D Graphics Primitives
----------------------

.. autoclass:: Spheres
   :members:

.. autoclass:: Lines
   :members:

.. autoclass:: Mesh
   :members:

.. autoclass:: ConvexPolyhedra
   :members:

.. autoclass:: ConvexSpheropolyhedra
   :members:

.. autoclass:: SpherePoints
   :members:


Matplotlib Backend
==================

.. automodule:: plato.draw.matplotlib

2D Graphics Primitives
----------------------

.. autoclass:: Disks
   :members:

.. autoclass:: Polygons
   :members:

.. autoclass:: Spheropolygons
   :members:

3D Graphics Primitives
----------------------

.. autoclass:: SpherePoints
   :members: