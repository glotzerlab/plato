.. plato documentation master file, created by
   sphinx-quickstart on Wed Aug 19 14:29:53 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=================================
Welcome to plato's documentation!
=================================

Plato is designed for efficient visualization of particle data. Think
of it sort of like matplotlib, but being less focused on 2D plotting.

Installation
============

You can install plato like this::

   $ git clone https://bitbucket.org/glotzer/plato.git
   $ # now install
   $ cd plato && pip install --user

.. note::

   If using conda or a virtualenv, the `--user` argument in the pip
   command above is unnecessary.

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

Manually-built versions are also uploaded periodically to
https://bitbucket.org/glotzer/plato/downloads/plato.pdf as well as
http://glotzerlab.engin.umich.edu/plato/ .

Contents:
=========

.. toctree::
   :maxdepth: 2

   primitives

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
