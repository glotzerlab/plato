import functools
import unittest
import vispy, vispy.app
import plato.draw.vispy as draw
import test_scenes
from test_internals import get_fname

class VispyTests(unittest.TestCase):

    def render(self, scene, num_run=0):
        fname = get_fname('vispy_{}.png'.format(num_run))
        scene.show()
        scene.save(fname)

for i, (name, scene) in enumerate(test_scenes.translate_usable_scenes(draw)):
    new_name = 'test_{}'.format(name)
    setattr(
        VispyTests, new_name, (lambda *args, scene=scene, num_run=i, **kwargs:
                               VispyTests.render(*args, scene=scene,
                                                 num_run=num_run)))
    getattr(VispyTests, new_name).__name__ = new_name

if __name__ == '__main__':
    unittest.main()
    vispy.app.run()
