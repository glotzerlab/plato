# README #

This is an in-progress work for updating plato for a 1.0 release. This release has a couple of high-level goals:

* Open-source the library (and split out the current plato.viz subpackage and modules system into a separate package)
* Convert the old `plato.gl` and `plato.export` capabilities to be on more equal footing: rather than favoring `vispy` as a live backend, have a set of backend-based subpackages that can be freely interchanged (to the extent that development of any particular backend has implemented some primitives)

## Expected (eventual) backends ##

* vispy
* matplotlib
* povray
* fresnel
* Desktop openGL
* javascript + webGL (static files as well as jupyter notebook integration)
* blender?
* unreal engine?

## To-do list

* Repair documentation on primitives, set up sphinx
* Add tests for individual backend APIs
* Strip graphics base, rename old plato project, and update it to use this library
