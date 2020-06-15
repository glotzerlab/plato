import functools
import unittest
import numpy as np
import os

import vispy, vispy.app
vispy_backend_name = os.environ.get('VISPY_TEST_BACKEND', None)
if vispy_backend_name:
    vispy.app.use_app(vispy_backend_name)

import plato
import plato.draw.vispy as draw
import test_scenes
from test_internals import get_fname

class VispyTests(unittest.TestCase):

    def render(self, scene, name=''):
        fname = get_fname('vispy_{}.png'.format(name))
        scene.show()
        if os.environ.get('LIVE_VISPY_TESTS', None):
            vispy.app.run()
        else:
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

    def test_normals_spheres(self):
        original_scene = test_scenes.colored_spheres()
        original_prim = list(original_scene)[0]

        features = dict(ambient_light=.25, render_normals=True)
        features['directional_light'] = .5*np.array([(.5, .25, -.5), (0, -.25, -.25)])
        rotation = [0.43797198, -0.4437895 ,  0.08068451,  0.7776423]

        prim = draw.Spheres.copy(original_prim)
        scene = draw.Scene(prim, features=features, rotation=rotation, zoom=4)

        self.render(scene, 'colored_spheres_normals')

    def test_normals_many_3d(self):
        features = dict(render_normals=True)

        num_particles = 3
        seed = 3

        np.random.seed(seed)
        positions = np.random.uniform(0, 3, (num_particles, 3))
        colors = np.random.uniform(.75, .9, (num_particles, 4))**1.5
        orientations = np.random.rand(num_particles, 4)
        orientations /= np.linalg.norm(orientations, axis=-1, keepdims=True)

        vertices = np.random.rand(12, 3)
        vertices -= np.mean(vertices, axis=0, keepdims=True)
        diameters = np.random.rand(num_particles)

        prim = draw.ConvexSpheropolyhedra(
            positions=positions, colors=colors, orientations=orientations,
            vertices=vertices, radius=.1)

        prim2 = draw.ConvexPolyhedra.copy(prim)
        prim2.positions = (-1, -1, -1) - prim2.positions

        prim3 = draw.Spheres.copy(prim)
        prim3.diameters = diameters
        prim3.positions = (1, -1, 1) - prim.positions

        # Lines doesn't currently support normals
        # prim4 = draw.Lines(start_points=prim.positions, end_points=prim2.positions,
        #                    colors=np.random.rand(num_particles, 4),
        #                    widths=np.ones((num_particles,))*.1)

        (vertices, faces) = plato.geometry.convexHull(vertices)
        vertices -= (-1, 1, -1)
        indices = list(plato.geometry.fanTriangleIndices(faces))
        colors = np.random.rand(len(vertices), 4)
        colors[:] = .5
        prim5 = draw.Mesh(vertices=vertices, indices=indices, colors=colors)

        prims = [prim, prim2, prim3, prim5]
        scene = draw.Scene(prims, zoom=5, clip_scale=10, features=features)

        self.render(scene, 'many_3d_normals')

for i, (name, scene) in enumerate(test_scenes.translate_usable_scenes(draw)):
    new_name = 'test_{}'.format(name)
    setattr(
        VispyTests, new_name, (lambda *args, scene=scene, name=name, **kwargs:
                               VispyTests.render(*args, scene=scene,
                                                 name=name)))
    getattr(VispyTests, new_name).__name__ = new_name

if os.environ.get('LIVE_VISPY_TESTS', None):
    for i, (name, scene) in enumerate(test_scenes.translate_usable_scenes(draw)):
        scene.enable('pick')
        new_name = 'test_pick_{}'.format(name)
        setattr(
            VispyTests, new_name, (lambda *args, scene=scene, name=name, **kwargs:
                                   VispyTests.render(*args, scene=scene,
                                                     name=name)))
        getattr(VispyTests, new_name).__name__ = new_name

if __name__ == '__main__':
    unittest.main()
