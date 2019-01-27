import unittest
import numpy as np
import numpy.testing as npt
import plato.draw as draw

class SceneTests(unittest.TestCase):
    def test_basic_size(self):
        test_size = (40, 50)
        test_pixel_scale = 32

        scene = draw.Scene(size=test_size, pixel_scale=test_pixel_scale)

        np.testing.assert_allclose(scene.size, test_size)
        np.testing.assert_allclose(
            np.array(scene.size)*test_pixel_scale, scene.size_pixels)

    def test_prim_container(self):
        disk_primitive = draw.Disks(
            positions=[[0, 0], [1, 2], [2, 4]],
            colors=[[1, 1, 0, 1], [0, 0, 1, 1], [0, 0, 0, 1]],
            radii=[1, 2, 3],
            outline=0.5
        )
        assert len(disk_primitive) == 3
        disk1 = disk_primitive[1]
        disk_reversed = disk_primitive[::-1]
        disk_masked = disk_primitive[[True, False, True]]
        assert len(disk1) == 1
        assert len(disk_reversed) == 3
        assert len(disk_masked) == 2
        npt.assert_almost_equal(disk1.positions, [[1, 2]])
        npt.assert_almost_equal(disk_reversed.colors,
                                [[0, 0, 0, 1], [0, 0, 1, 1], [1, 1, 0, 1]])
        npt.assert_almost_equal(disk_masked.radii, [1, 3])

        # Ensure that length corresponds to the size of the
        # shortest per-particle property array
        disk_primitive = draw.Disks(
            positions=[[0, 0], [1, 2], [2, 4]],
            colors=[[1, 1, 0, 1], [0, 0, 1, 1]],
            radii=[1, 2, 3],
            outline=0.5
        )
        assert len(disk_primitive) == 2

    def test_add_remove_prims(self):
        prim1 = draw.Disks()
        prim2 = draw.Spheres()

        scene = draw.Scene(prim1)
        self.assertIn(prim1, scene)
        self.assertNotIn(prim2, scene)

        scene.add_primitive(prim2)
        self.assertIn(prim2, scene)

        scene.remove_primitive(prim2)
        self.assertNotIn(prim2, scene)

        with self.assertRaises(ValueError):
            scene.remove_primitive(prim2)

        # shouldn't encounter exception with strict mode disabled
        scene.remove_primitive(prim2, strict=False)

        # prim1 should still be there
        self.assertIn(prim1, scene)

    def test_features(self):
        scene = draw.Scene(features=dict(test1=13, test2=dict(test_name='test2')))

        self.assertIn('test1', scene.enabled_features)
        self.assertIn('test2', scene.enabled_features)
        self.assertNotIn('test3', scene.enabled_features)

        self.assertEqual(scene.get_feature_config('test1'), {'value': 13})
        self.assertEqual(scene.get_feature_config('test2'), {'test_name': 'test2'})
        self.assertEqual(scene.get_feature_config('test3'), None)

        scene.enable('test3', 'auto_value', value='discard', another_value=None)
        self.assertIn('test3', scene.enabled_features)
        self.assertEqual(
            scene.get_feature_config('test3'),
            {'value': 'auto_value', 'another_value': None})

if __name__ == '__main__':
    unittest.main()
