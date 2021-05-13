import os
import unittest
from test_internals import get_fname

from nbconvert.nbconvertapp import NbConvertApp

class PythreejsTests(unittest.TestCase):

    def test_notebook(self):
        src = os.path.join(os.pardir, 'examples', 'pythreejs test scenes.ipynb')
        fname = get_fname('pythreejs_test_scenes.html')

        NbConvertApp.launch_instance(
            argv=['--execute', '--to', 'html', '--output', fname, src])

if __name__ == '__main__':
    unittest.main()
