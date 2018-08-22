=================================
Welcome to plato's documentation!
=================================

Plato is designed for efficient visualization of particle data. Think
of it sort of like matplotlib, but being less focused on 2D plotting.

Installation
============

Plato is available on PyPI for installation via pip::

  $ pip install plato-draw

You can also install plato from source, like this::

   $ git clone https://bitbucket.org/glotzer/plato.git
   $ # now install
   $ cd plato && python setup.py install

.. note::

   Depending on which backends you want to use, there may be
   additional steps required; see the section on interactive backends
   below.

Using Interactive Backends
--------------------------

Plato contains a number of backends, each with its own set of
dependencies. Getting the vispy backend working for both the desktop
and jupyter notebook can be tricky. To help users install its
dependencies, we keep some advice `here
<https://bitbucket.org/snippets/glotzer/nMg8Gr/plato-dependency-installation-tips>`_
regarding particular known-good versions of dependencies for pip and
conda.

Documentation
=============

The documentation is available as standard sphinx documentation::

  $ cd doc
  $ make html

Automatically-built documentation is available at
https://plato-draw.readthedocs.io .

Examples
========

Several usage examples are available. Many simple, but less
interesting, scenes can be found in `the test demo scene script
<https://bitbucket.org/glotzer/plato/src/master/test/test_scenes.py>`_. Somewhat
less transparent examples can be found in `the plato-gallery
repository <https://bitbucket.org/glotzer/plato-gallery>`_.

Contents:
=========

.. toctree::
   :maxdepth: 2

   primitives
   matplotlib
   povray
   vispy
   troubleshooting

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
