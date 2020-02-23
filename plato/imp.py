"""
The `imp` module defines an imperative API for convenient,
immediate visualization of results without directly creating separate
primitive and scene objects. The set of available primitives and
attributes are the same as in :py:mod:`plato.draw`, but the functions
in this module are named as lowercase_with_underscores rather than
CamelCase class names. Final scenes can be shown either directly,
allowing for more careful selection of backends and passing arguments
to the underlying scene by using :py:func:`show` or automatically by
using the `plato.imp` IPython extension.

Examples::

    import plato.imp as imp
    imp.spheres(positions=[1, 0, 0])
    imp.lines(start_points=(0, 1, 0), end_points=(1, 0, 0))
    imp.show(backend='zdog', zoom=10)

    # the line below causes cell contents to automatically be shown in jupyter notebooks
    %load_ext plato.imp
    imp.polygons(outline=.1)
    imp.arrows_2D(positions=(-1, 0))

"""
import functools
import importlib
import sys

from . import draw

_pending_primitives = []
_last_scene = None
_used_vispy_backend = None

_2d_primitives = (
    draw.Arrows2D,
    draw.Disks,
    draw.DiskUnions,
    draw.Polygons,
    draw.Spheropolygons,
    draw.Voronoi,
)

class _IPythonCallbacks(object):
    def __init__(self, ip):
        self.shell = ip

    def post_run_cell(self, result):
        if _pending_primitives:
            show()

def clear():
    """Clears the imperative state."""
    global _last_scene

    _pending_primitives.clear()
    _last_scene = None

def _get_backend(backend, scene):
    global _used_vispy_backend
    if backend is None:
        backend = _guess_backend(scene)

    if backend.startswith('vispy_'):
        if _used_vispy_backend is None:
            vispy_backend = backend[len('vispy_'):]
            import vispy, vispy.app
            try:
                vispy.app.use_app(vispy_backend)
                _used_vispy_backend = vispy_backend
            except RuntimeError:
                _used_vispy_backend = vispy.app.use_app()
        backend = 'vispy'

    module_name = 'plato.draw.{}'.format(backend)
    return importlib.import_module(module_name)

def _get_scene(backend=None, **kwargs):
    global _last_scene
    pure_scene = draw.Scene(list(_pending_primitives), **kwargs)
    backend = _get_backend(backend, pure_scene)
    scene = _last_scene = pure_scene.convert(backend)

    if any(isinstance(prim, _2d_primitives) for prim in _pending_primitives):
        scene.enable('pan', True)
    _pending_primitives.clear()

    return scene

def get(backend=None, **kwargs):
    """Returns the last-shown imperative scene, or creates a new one.

    This method returns the most recent scene, either that has been
    shown via a call to `show()` or defined by calling
    primitive-creating functions. If a new scene is created, the user
    is responsible for calling `Scene.show()` as appropriate.
    """
    if _last_scene is None or _pending_primitives:
        _get_scene(backend, **kwargs)
    return _last_scene

def _guess_backend(scene):
    classes = [type(prim) for prim in scene]
    backends = ['vispy', 'pythreejs', 'povray', 'fresnel', 'matplotlib', 'zdog']

    for backend in backends:
        try:
            module_name = 'plato.draw.{}'.format(backend)
            module = importlib.import_module(module_name)

            # use the notebook backend by default
            if backend == 'vispy' and 'ipykernel' in sys.modules:
                backend = 'vispy_ipynb_webgl'

            if all(hasattr(module, cls.__name__) for cls in classes):
                return backend
        except ImportError:
            continue

    msg = 'No backends were usable that support these classes: {}'.format(classes)
    raise RuntimeError(msg)

def load_ipython_extension(ip):
    cb = _IPythonCallbacks(ip)
    ip.events.register('post_run_cell', cb.post_run_cell)

def _shape_dispatcher(cls, *args, **kwargs):
    result = cls(*args, **kwargs)
    _pending_primitives.append(result)
    return result

def _shape_generator(cls):
    result = functools.partial(_shape_dispatcher, cls)
    result = functools.update_wrapper(result, cls)

    doc = result.__doc__ or ''
    result.__doc__ = ('Generates and immediately displays the object described '
                      'below.\n\n' + doc)

    return result

def show(backend=None, **kwargs):
    """Immediately show all pending primitives that have been created.

    A backend name can optionally be specified, but all other keyword
    arguments are passed to the :py:class:`plato.draw.Scene`
    constructor. If no backend is specified, a backend that can be
    imported and supports all the pending primitives will be selected.
    """
    scene = _get_scene(backend, **kwargs)
    scene.show()

arrows2D = arrows_2D = _shape_generator(draw.Arrows2D)
box = _shape_generator(draw.Box)
convex_polyhedra = _shape_generator(draw.ConvexPolyhedra)
convex_spheropolyhedra = _shape_generator(draw.ConvexSpheropolyhedra)
disks = _shape_generator(draw.Disks)
disk_unions = _shape_generator(draw.DiskUnions)
ellipsoids = _shape_generator(draw.Ellipsoids)
lines = _shape_generator(draw.Lines)
mesh = _shape_generator(draw.Mesh)
polygons = _shape_generator(draw.Polygons)
sphere_points = _shape_generator(draw.SpherePoints)
spheres = _shape_generator(draw.Spheres)
sphere_unions = _shape_generator(draw.SphereUnions)
spheropolygons = _shape_generator(draw.Spheropolygons)
voronoi = _shape_generator(draw.Voronoi)
