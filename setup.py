#!/usr/bin/env python

import os
from setuptools import setup

with open('plato/version.py') as version_file:
    exec(version_file.read())

long_description_lines = []
with open(os.path.join('doc', 'source', 'index.rst'), 'r') as readme:
    for line in readme:
        if line.startswith('Contents'):
            break
        long_description_lines.append(line)
long_description = ''.join(long_description_lines)

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
