import unittest
import plato.draw.povray as draw
import test_scenes


class PovrayTests(unittest.TestCase):

    def render(self, scene, num_run=0):
        fname = '/tmp/{}.png'.format(num_run)
        scene.save(fname)

for i, (name, scene) in enumerate(test_scenes.translate_usable_scenes(draw)):
    new_name = 'test_{}'.format(name)
    setattr(
        PovrayTests, new_name, (lambda *args, scene=scene, num_run=i, **kwargs:
                                PovrayTests.render(*args, scene=scene,
                                                   num_run=num_run)))
    getattr(PovrayTests, new_name).__name__ = new_name

if __name__ == '__main__':
    unittest.main()
