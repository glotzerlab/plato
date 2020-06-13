=======================
Troubleshooting and FAQ
=======================

.. note::

   Depending on which backends you want to use, there may be
   additional steps required for installation; consult the advice
   `here
   <https://bitbucket.org/snippets/glotzer/nMg8Gr/plato-dependency-installation-tips>`_.

Jupyter Notebook Issues
=======================

**When starting a jupyter notebook, I get a "Permission denied" error for a linking operation.**

This may be related to jupyter upgrades. Manually remove the symlink
and the notebook should be able to proceed once more.

**When running in a jupyter notebook, nothing is displayed.**

The solution to this problem depends on more details.

- *The canvas is displayed entirely black with "Uncaught TypeError: Cannot read property 'handle' of undefined" (or similar language)*: After the `canvas.show()` command in the cell, add a line `import time;time.sleep(.1)`. You may need to increase the argument of `time.sleep()`. This is due to a race condition in vispy.
- *I get an error 404 in the browser console for vispy.min.js* - Make sure that jupyter, ipywidgets, and all of the jupyter components are up to date (and have compatible versions, see https://bitbucket.org/snippets/glotzer/nMg8Gr/plato-dependency-installation-tips ).
- *I get an error 404 in the browser console for webgl-backend.js* - Try removing your jupyter notebook cache (~/.jupyter and ~/Library/Jupyter on OSX) and restarting jupyter
- Make sure the `jupyter` executable you are using is in the same virtualenv or conda environment as plato and its dependencies

**Things aren't displayed and I get a message "zmq message arrived on closed channel" in the console.**

Try running your jupyter notebook command with an increased data rate
limit::

  jupyter notebook --NotebookApp.iopub_data_rate_limit=1000000000
