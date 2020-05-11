[![PyPI](https://img.shields.io/pypi/v/plato-draw.svg?style=flat)](https://pypi.org/project/plato-draw/)
[![ReadTheDocs](https://img.shields.io/readthedocs/plato-draw.svg?style=flat)](https://plato-draw.readthedocs.io/en/latest/)
[![CircleCI](https://img.shields.io/circleci/project/github/glotzerlab/plato/master.svg?style=flat)](https://circleci.com/gh/glotzerlab/plato)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/glotzerlab/plato/master?filepath=examples)

# Introduction

Plato is designed for efficient visualization of particle data:
collections of particles that may be colored or oriented
differently. It fills a similar role as matplotlib, but is less
focused on 2D plotting. It supports a variety of backends with
different capabilities and use cases, ranging from interactive
visualization in the desktop or jupyter notebooks to high-quality,
static raytraced and vector images for publication.

# Installation

Plato is available on PyPI for installation via pip:

```
$ pip install plato-draw
```

You can also install plato from source, like this:

```
$ git clone https://github.com/glotzerlab/plato.git
$ # now install
$ cd plato && python setup.py install
```

**Note**: Depending on which backends you want to use, there may be
additional steps required; see the section on interactive backends
below.

## Using Interactive Backends

Plato supports a number of backends, each with its own set of
dependencies. Getting the vispy backend working for both the desktop
and jupyter notebook can be tricky. Make sure to check the official
[vispy documentation](http://vispy.org/installation.html). We also
keep some advice
[here](https://bitbucket.org/snippets/glotzer/nMg8Gr/plato-dependency-installation-tips)
regarding particular known-good versions of dependencies for pip and
conda.

# Documentation

The documentation is available as standard sphinx documentation:

```
$ cd doc
$ pip install -r requirements.txt
$ make html
```

Automatically-built documentation is available at
https://plato-draw.readthedocs.io .

# Examples

Several usage examples are available. Many simple, but less
interesting, scenes can be found in [the test demo scene
script](https://github.com/glotzerlab/plato/blob/master/test/test_scenes.py),
available as [live examples on
mybinder.org](https://mybinder.org/v2/gh/glotzerlab/plato/master?filepath=examples). Somewhat
less transparent examples can be found in [the plato-gallery
repository](https://github.com/glotzerlab/plato-gallery).
