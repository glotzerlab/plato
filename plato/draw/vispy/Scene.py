import functools
import logging

import numpy as np
import vispy.io

from .Canvas import Canvas
from ... import draw
from ..Scene import DEFAULT_DIRECTIONAL_LIGHTS

logger = logging.getLogger(__name__)

def set_orthographic_projection(camera, left, right, bottom, top, near, far):
    camera[:] = 0
    camera[0, 0] = 2/(right - left)
    camera[3, 0] = -(right + left)/(right - left)
    camera[1, 1] = 2/(top - bottom)
    camera[3, 1] = -(top + bottom)/(top - bottom)
    camera[2, 2] = -2/(far - near)
    camera[3, 2] = -(far + near)/(far - near)
    camera[3, 3] = 1

def selection_point(callback, scene, start, end, units='scene', **kwargs):
    point = scene.transform(end, 'pixels_gui', units)
    callback(point, **kwargs)

def selection_rectangle(callback, scene, start, end, units='scene', **kwargs):
    points = scene.transform([start, end], 'pixels_gui', units)
    callback(points[0], points[1], **kwargs)

class Scene(draw.Scene):
    __doc__ = (draw.Scene.__doc__ or '') + """
    This Scene supports the following features:

    * *pan*: If enabled, mouse movement will translate the scene instead of rotating it.
    * *directional_light*: Add directional lights. The given value indicates the magnitude*direction normal vector.
    * *ambient_light*: Enable trivial ambient lighting. The given value indicates the magnitude of the light (in [0, 1]).
    * *translucency*: Enable order-independent transparency rendering.
    * *fxaa*: Enable fast approximate anti-aliasing.
    * *ssao*: Enable screen space ambient occlusion.
    * *additive_rendering*: Enable additive rendering. This mode is good for visualizing densities projected through the viewing direction. Takes an optional 'invert' argument to invert the additive rendering (i.e., black-on-white instead of white-on-black).
    * *outlines*: Enable cartoony outlines. The given value indicates the width of the outlines (start small, perhaps 1e-5 to 1e-3).
    * *pick*: Select a single particle with the mouse on the next mouse click. The given callback function receives the scene, primitive index within the scene, and shape index within the primitive that are selected. If no particle is selected, the callback is not run but pick mode remains enabled until a particle is selected; to disable this behavior, set the optional `persist` argument to False.
    * *select_point*: Perform a callback on the next mouse click. The callback receives the clicked position (in the coordinate system of the scene unless the 'units' parameter is set to another valid target for :py:meth:`Scene.transform`) and any additional keyword arguments passed in the feature config.
    * *select_rect*: Perform a callback on the next mouse drag event. The callback receives the start and end point of the selected area (in the coordinate system of the scene unless the 'units' parameter is set to another valid target for :py:meth:`Scene.transform`) and any additional keyword arguments passed in the feature config.
    * *static*: Enable static rendering. When possible (when vispy is using a non-notebook backend), display a statically-rendered image of a scene instead of the live webGL version when `Scene.show()` is called.
    """

    # features that should be carefully enabled only once for the scene at a time
    _PROTECTED_FEATURES = {'select_point', 'select_rect', 'pick'}

    def __init__(self, *args, canvas_kwargs={}, **kwargs):
        self.camera = np.eye(4, dtype=np.float32)
        self._zoom = 1
        self._pixel_scale = 1
        self._clip_scale = 1
        self._translation = [0, 0, 0]
        self._canvas = None
        super(Scene, self).__init__(*args, **kwargs)
        self._canvas = Canvas(self, **canvas_kwargs)
        # there is a cyclic dependency: many features depend on having
        # a canvas initialized, but the canvas is what determines some
        # of our attributes. Here we re-enable features that may have
        # been skipped the first time around.
        for (name, params) in list(self._enabled_features.items()):
            self.enable(name, **params)

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        self._zoom = value
        self._update_camera()

    @property
    def pixel_scale(self):
        return self._pixel_scale

    @pixel_scale.setter
    def pixel_scale(self, value):
        self._pixel_scale = value
        if self._canvas is not None:
            self._canvas.size = self.size_pixels.astype(np.uint32)
        self._update_camera()

    @property
    def clip_scale(self):
        return self._clip_scale

    @clip_scale.setter
    def clip_scale(self, value):
        self._clip_scale = value
        self._update_camera()

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size[:] = value
        self._update_camera()

    def add_primitive(self, primitive):
        super(Scene, self).add_primitive(primitive)
        self._update_camera()
        for feature in list(self.enabled_features):
            if feature in self._PROTECTED_FEATURES:
                continue
            self.enable(feature, **self.get_feature_config(feature))

    def enable(self, name, auto_value=None, **parameters):
        """Enable an optional rendering feature.

        :param name: Name of the feature to enable
        :param auto_value: Shortcut for features with single-value configuration. If given as a positional argument, will be given the default configuration name 'value'.
        :param parameters: Keyword arguments specifying additional configuration options for the given feature
        """
        if auto_value is not None:
            parameters['value'] = auto_value

        if name == 'directional_light':
            lights = parameters.get('value', DEFAULT_DIRECTIONAL_LIGHTS)
            lights = np.atleast_2d(lights).astype(np.float32)
            for prim in self._primitives:
                prim.diffuseLight = lights

        elif name == 'ambient_light':
            light = parameters.get('value', .25)
            for prim in self._primitives:
                prim.ambientLight = light

        elif name == 'select_point':
            try:
                callback_kwargs = dict(parameters)
                callback = callback_kwargs.pop('value')
            except KeyError:
                raise ValueError(
                    'A callback must be given for the select_point feature')

            callback = functools.partial(
                selection_point, callback, self, **callback_kwargs)
            if self._canvas is not None:
                self._canvas.grab_selection_area(callback)

        elif name == 'select_rect':
            try:
                callback_kwargs = dict(parameters)
                callback = callback_kwargs.pop('value')
            except KeyError:
                raise ValueError(
                    'A callback must be given for the select_rect feature')

            callback = functools.partial(
                selection_rectangle, callback, self, **callback_kwargs)
            if self._canvas is not None:
                self._canvas.grab_selection_area(callback)

        if self._canvas is not None:
            if name in self._canvas._VALID_FEATURES:
                self._canvas._enable_feature(**{name: parameters})

        super(Scene, self).enable(name, **parameters)

    def disable(self, name, strict=True):
        if self._canvas is not None:
            if name in self._canvas._VALID_FEATURES:
                self._canvas._disable_feature(name)

        super(Scene, self).disable(name, strict=strict)

    def _update_camera(self):
        (width, height) = self.size.astype(np.float32)

        dz = np.sqrt(np.sum(self.size**2))*self._clip_scale

        translation = self.translation
        translation[2] = -(2 + dz)/2
        self.translation = translation

        set_orthographic_projection(
            self.camera,
            -width/2, width/2,
            -height/2, height/2,
            1, 1 + dz)

        if self._canvas is not None:
            self._canvas.clip_planes = (1, 1 + dz)

        self.camera[[0, 1], [0, 1]] *= self._zoom

        for prim in self._primitives:
            prim.camera = self.camera

    def save(self, filename):
        """Render and save an image of this Scene.

        :param filename: target filename to save the image into
        """
        if self._canvas is not None:
            img = self._canvas.render()
            vispy.io.write_png(filename, img)

    def show(self):
        """Display this Scene object."""
        cfg = self.get_feature_config('static')

        if cfg and cfg.get('value', False):
            import imageio
            import io
            import IPython.display
            import vispy.app

            vispy_backend = vispy.app.use_app().backend_name
            if 'webgl' not in vispy_backend:
                target = io.BytesIO()
                img = self._canvas.render()
                imageio.imwrite(target, img, 'png')
                to_display = IPython.display.Image(data=target.getvalue())
                return IPython.display.display(to_display, display_id=str(id(self)))

            msg = ('vispy has already loaded the {} backend, ignoring static'
                   ' feature. Try manually selecting a desktop vispy backend '
                   'before importing plato, for example:\n    import vispy.app; '
                   'vispy.app.use_app("pyglet")'.format(vispy_backend))
            logger.warning(msg)

        return self._canvas.show()

    def render(self):
        """Have vispy redraw this Scene object."""
        self._canvas.update()

    def _ipython_display_(self):
        return self.show()
