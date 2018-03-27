import unittest
import plato.draw.povray as draw
import test_scenes

class PovrayTests(unittest.TestCase):
    NUM_RUN = 0

    def render(self, scene):
        fname = '/tmp/{}.png'.format(self.NUM_RUN)
        self.NUM_RUN += 1
        scene.save(fname)

for (name, scene) in test_scenes.translate_usable_scenes(draw):
    new_name = 'test_{}'.format(name)
    setattr(
        PovrayTests, new_name, (lambda *args, scene=scene, **kwargs:
                                PovrayTests.render(*args, scene=scene)))
    getattr(PovrayTests, new_name).__name__ = new_name

if __name__ == '__main__':
    unittest.main()
