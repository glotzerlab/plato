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

   $ git clone https://github.com/glotzerlab/plato.git
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
and jupyter notebook can be tricky. Make sure to check the official
`vispy documentation <http://vispy.org/installation.html>`_. We also
keep some advice `here
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
<https://github.com/glotzerlab/plato/blob/master/test/test_scenes.py>`_,
available as `live examples on mybinder.org
<https://mybinder.org/v2/gh/glotzerlab/plato/master?filepath=examples>`_. Somewhat
less transparent examples can be found in `the plato-gallery
repository <https://github.com/glotzerlab/plato-gallery>`_.

Contents:
=========

.. toctree::
   :maxdepth: 2

   primitives
   fresnel
   matplotlib
   povray
   pythreejs
   vispy
   zdog
   imperative
   troubleshooting

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
