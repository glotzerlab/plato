#!/usr/bin/env python

long_description="""
Plato is designed for efficient visualization of particle data. Think
of it sort of like matplotlib, but being less focused on 2D plotting.

Documentation
=============

Full documentation is available in standard sphinx form::

  $ cd doc
  $ make html

Automatically-built documentation is available at
https://plato-draw.readthedocs.io .
"""

from setuptools import setup

with open('plato/version.py') as version_file:
    exec(version_file.read())

setup(name='plato-draw',
      author='Matthew Spellings',
      author_email='mspells@umich.edu',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Topic :: Multimedia :: Graphics',
          'Topic :: Scientific/Engineering :: Visualization'
      ],
      description='Geometry and visualization tools for collections of particles',
      install_requires=['numpy', 'scipy', 'rowan'],
      license='BSD',
      long_description=long_description,
      packages=[
          'plato', 'plato.draw',
          'plato.draw.blender',
          'plato.draw.matplotlib',
          'plato.draw.povray',
          'plato.draw.vispy'
      ],
      project_urls={
          'Documentation': 'http://plato-draw.readthedocs.io/',
          'Source': 'https://bitbucket.org/glotzer/plato'
          },
      python_requires='>=3',
      version=__version__
      )
