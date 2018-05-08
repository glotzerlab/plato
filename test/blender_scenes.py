"""This file doesn't use any sort of standard unit test framework
because of how blender invocation typically works. The tests can be
run as:

  PYTHONPATH="$(pwd):${PYTHONPATH}" blender --background --python blender_scenes.py

"""

import plato.draw.blender as draw
import test_scenes
from test_internals import get_fname

def render(scene, name=''):
    fname = get_fname('blender_{}.png'.format(name))
    scene.save(fname)

for i, (name, scene) in enumerate(test_scenes.translate_usable_scenes(draw)):
    render(scene, name)
