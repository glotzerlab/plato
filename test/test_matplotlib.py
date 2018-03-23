import functools
import unittest
import matplotlib, matplotlib.pyplot as pp
import plato.draw.matplotlib as draw
import test_scenes

class MatplotlibTests(unittest.TestCase):
    def render(self, scene):
        (fig, _) = scene.render()
        pp.show(block=True)

for (name, scene) in test_scenes.translate_usable_scenes(draw):
    new_name = 'test_{}'.format(name)
    setattr(
        MatplotlibTests, new_name, (lambda *args, scene=scene, **kwargs:
                                    MatplotlibTests.render(*args, scene=scene)))
    getattr(MatplotlibTests, new_name).__name__ = new_name

if __name__ == '__main__':
    unittest.main()
