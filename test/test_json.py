import unittest
import plato.draw.json as draw
import test_scenes


class JSONTests(unittest.TestCase):

    def render(self, scene, num_run=0):
        fname = '/tmp/{}.json'.format(num_run)
        with open(fname, 'w') as outfile:
            outfile.write(scene.render())

for i, (name, scene) in enumerate(test_scenes.translate_usable_scenes(draw)):
    new_name = 'test_{}'.format(name)
    setattr(
        JSONTests, new_name, (lambda *args, scene=scene, num_run=i, **kwargs:
                              JSONTests.render(*args, scene=scene,
                                               num_run=num_run)))
    getattr(JSONTests, new_name).__name__ = new_name

if __name__ == '__main__':
    unittest.main()
