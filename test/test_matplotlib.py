import unittest
import matplotlib; matplotlib.use('AGG')
import plato.draw.matplotlib as draw
import test_scenes

class MatplotlibTests(unittest.TestCase):

    def render(self, scene, num_run=0):
        fname = '/tmp/matplotlib_{}.png'.format(num_run)
        scene.save(fname)

for i, (name, scene) in enumerate(test_scenes.translate_usable_scenes(draw)):
    new_name = 'test_{}'.format(name)
    setattr(
        MatplotlibTests, new_name, (lambda *args, scene=scene, num_run=i, **kwargs:
                                    MatplotlibTests.render(*args, scene=scene,
                                                           num_run=num_run)))
    getattr(MatplotlibTests, new_name).__name__ = new_name

if __name__ == '__main__':
    unittest.main()
