import unittest
import plato.draw as draw

class PrimitiveLenTests(unittest.TestCase):
    def test_Spheres(self):
        for N in range(1, 3):
            kwargs = dict(positions=N*[(0, 0, 0)],
                          colors=N*[(1, 1, 1, 1)],
                          radii=N*[1])
            prim = draw.Spheres(**kwargs)
            self.assertEqual(len(prim), N)

    def test_Box(self):
        prim = draw.Box(Lx=3)
        self.assertEqual(len(prim), 12)

if __name__ == '__main__':
    unittest.main()
