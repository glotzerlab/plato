import functools
import unittest
import vispy, vispy.app
import plato.draw.vispy as draw
import test_scenes

class VispyTests(unittest.TestCase):
    def render(self, scene):
        scene.show()
        vispy.app.run()

for (name, scene) in test_scenes.translate_usable_scenes(draw):
    new_name = 'test_{}'.format(name)
    setattr(
        VispyTests, new_name, (lambda *args, scene=scene, **kwargs:
                               VispyTests.render(*args, scene=scene)))
    getattr(VispyTests, new_name).__name__ = new_name

if __name__ == '__main__':
    unittest.main()
