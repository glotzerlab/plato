import logging
import unittest
import plato.draw.fresnel as draw
import subprocess
import test_scenes
from test_internals import get_fname

logger = logging.getLogger(__name__)


class FresnelTests(unittest.TestCase):

    def render(self, scene, name=''):
        fname = get_fname('fresnel_{}.png'.format(name))
        scene.save(fname)

for i, (name, scene) in enumerate(test_scenes.translate_usable_scenes(draw)):
    new_name = 'test_{}'.format(name)
    print(new_name)
    setattr(
        FresnelTests, new_name, (lambda *args, scene=scene, name=name, **kwargs:
                                 FresnelTests.render(*args, scene=scene,
                                                     name=name)))
    getattr(FresnelTests, new_name).__name__ = new_name

if __name__ == '__main__':
    unittest.main()
