import unittest
import matplotlib; matplotlib.use('AGG')
import plato.draw.matplotlib as draw
import test_scenes
from test_internals import get_fname

class MatplotlibTests(unittest.TestCase):

    def render(self, scene, name=''):
        fname = get_fname('matplotlib_{}.png'.format(name))
        scene.save(fname)

for i, (name, scene) in enumerate(test_scenes.translate_usable_scenes(draw)):
    new_name = 'test_{}'.format(name)
    setattr(
        MatplotlibTests, new_name, (lambda *args, scene=scene, name=name, **kwargs:
                                    MatplotlibTests.render(*args, scene=scene,
                                                           name=name)))
    getattr(MatplotlibTests, new_name).__name__ = new_name

if __name__ == '__main__':
    unittest.main()
