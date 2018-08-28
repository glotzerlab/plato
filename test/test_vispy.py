import functools
import unittest
import numpy as np
import vispy, vispy.app
import plato.draw.vispy as draw
import test_scenes
from test_internals import get_fname

class VispyTests(unittest.TestCase):

    def render(self, scene, name=''):
        fname = get_fname('vispy_{}.png'.format(name))
        scene.show()
        scene.save(fname)
        scene._canvas.close()
        vispy.app.process_events()

    def test_fxaa_ssao(self):
        original_scene = test_scenes.colored_spheres()
        original_prim = list(original_scene)[0]

        features = dict(ambient_light=.25)
        features['directional_light'] = .5*np.array([(.5, .25, -.5), (0, -.25, -.25)])
        rotation = [0.43797198, -0.4437895 ,  0.08068451,  0.7776423]

        prim = draw.Spheres.copy(original_prim)
        scene = draw.Scene(prim, features=features, rotation=rotation, zoom=4)
        scene.enable('fxaa')
        scene.enable('ssao')

        self.render(scene, 'colored_spheres_fxaa_ssao')

    def test_ssao_fxaa(self):
        original_scene = test_scenes.colored_spheres()
        original_prim = list(original_scene)[0]

        features = dict(ambient_light=.25)
        features['directional_light'] = .5*np.array([(.5, .25, -.5), (0, -.25, -.25)])
        rotation = [0.43797198, -0.4437895 ,  0.08068451,  0.7776423]

        prim = draw.Spheres.copy(original_prim)
        scene = draw.Scene(prim, features=features, rotation=rotation, zoom=4)
        scene.enable('ssao')
        scene.enable('fxaa')

        self.render(scene, 'colored_spheres_ssao_fxaa')

for i, (name, scene) in enumerate(test_scenes.translate_usable_scenes(draw)):
    new_name = 'test_{}'.format(name)
    setattr(
        VispyTests, new_name, (lambda *args, scene=scene, name=name, **kwargs:
                               VispyTests.render(*args, scene=scene,
                                                 name=name)))
    getattr(VispyTests, new_name).__name__ = new_name

if __name__ == '__main__':
    unittest.main()
