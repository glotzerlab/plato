"""This file doesn't use any sort of standard unit test framework
because of how blender invocation typically works. The tests can be
run as:

  PYTHONPATH="$(pwd):${PYTHONPATH}" blender --background --python test_blender.py

"""

import plato.draw.blender as draw
import test_scenes

def render(scene, num_run=0):
    fname = '/tmp/blender_{}.png'.format(num_run)
    scene.save(fname)

for i, (name, scene) in enumerate(test_scenes.translate_usable_scenes(draw)):
    render(scene, i)
