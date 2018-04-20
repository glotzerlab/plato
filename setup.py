#!/usr/bin/env python

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
      install_requires=['numpy', 'scipy'],
      license='BSD',
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
