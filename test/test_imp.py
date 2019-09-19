import os
import unittest
import vispy, vispy.app
vispy_backend_name = os.environ.get('VISPY_TEST_BACKEND', None)
if vispy_backend_name:
    vispy.app.use_app(vispy_backend_name)
import plato.imp as imp

class SceneTests(unittest.TestCase):
    def tearDown(self):
        imp.clear()

    def test_basic(self):
        imp.spheres()
        imp.convex_polyhedra()

        scene = imp.get()
        self.assertEqual(len(scene), 2)

        # calling get() without making new primitives returns the same scene...
        scene = imp.get()
        self.assertEqual(len(scene), 2)

        # but adding a new primitive returns a new scene
        imp.spheres()
        scene = imp.get()
        self.assertEqual(len(scene), 1)

    def test_2d_pan(self):
        imp.arrows_2D()
        imp.disks()
        imp.disk_unions()
        imp.polygons()
        imp.spheropolygons()
        imp.voronoi()

        scene = imp.get()
        pan_enabled = scene.get_feature_config('pan')
        self.assertIsNotNone(pan_enabled)

if __name__ == '__main__':
    unittest.main()
