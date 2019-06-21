import unittest
import plato.draw.zdog as draw
import test_scenes
from test_internals import get_fname

class ZdogTests(unittest.TestCase):

    def render(self, scene, name=''):
        fname = get_fname('zdog_{}.html'.format(name))
        scene.save(fname)

for i, (name, scene) in enumerate(test_scenes.translate_usable_scenes(draw)):
    new_name = 'test_{}'.format(name)
    setattr(
        ZdogTests, new_name, (lambda *args, scene=scene, name=name, **kwargs:
                                ZdogTests.render(*args, scene=scene,
                                                   name=name)))
    getattr(ZdogTests, new_name).__name__ = new_name

if __name__ == '__main__':
    unittest.main()
