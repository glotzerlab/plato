import logging
import unittest
import plato.draw.povray as draw
import subprocess
import test_scenes
from test_internals import get_fname

logger = logging.getLogger(__name__)

try:
    subprocess.check_call(['povray', '-h'])
    suffix = 'png'
except FileNotFoundError:
    logger.warning('Couldn\'t find povray executable, saving .pov instead')
    suffix = 'pov'

class PovrayTests(unittest.TestCase):

    def render(self, scene, num_run=0):
        fname = get_fname('povray_{}.{}'.format(num_run, suffix))
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
