#!/usr/bin/env python

from setuptools import setup

with open('plato/version.py') as version_file:
    exec(version_file.read())

setup(name='plato',
      version=__version__,
      description='Geometry and visualization tools',
      author='Matthew Spellings',
      author_email='mspells@umich.edu',
      classifiers=[
          'License :: OSI Approved :: BSD License'
      ],
      packages=[
          'plato', 'plato.draw',
          'plato.draw.blender',
          'plato.draw.matplotlib',
          'plato.draw.povray',
          'plato.draw.vispy'
      ],
      install_requires=['numpy', 'scipy']
      )
