#!/usr/bin/env python

import os
from setuptools import setup

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

version_fname = os.path.join(THIS_DIR, 'plato', 'version.py')
with open(version_fname) as version_file:
    exec(version_file.read())

readme_fname = os.path.join(THIS_DIR, 'README.md')
with open(readme_fname) as readme_file:
    long_description = readme_file.read()

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
      extras_require={
          'pyside': ['pyside', 'vispy >= 0.5.3'],
          'pyside2': ['pyside2', 'vispy >= 0.6'],
          'pythreejs': ['pythreejs'],
      },
      install_requires=['numpy', 'scipy', 'rowan'],
      license='BSD-3-Clause',
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages=[
          'plato', 'plato.draw',
          'plato.draw.blender',
          'plato.draw.fresnel',
          'plato.draw.matplotlib',
          'plato.draw.povray',
          'plato.draw.pythreejs',
          'plato.draw.vispy',
          'plato.draw.zdog',
      ],
      project_urls={
          'Documentation': 'http://plato-draw.readthedocs.io/',
          'Source': 'https://github.com/glotzerlab/plato'
          },
      python_requires='>=3',
      version=__version__
      )
