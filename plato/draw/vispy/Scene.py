import vispy.io
from .Canvas import Canvas
from ... import draw
import numpy as np
from .internal import DEFAULT_DIRECTIONAL_LIGHTS

def set_orthographic_projection(camera, left, right, bottom, top, near, far):
    camera[:] = 0
    camera[0, 0] = 2/(right - left)
    camera[3, 0] = -(right + left)/(right - left)
    camera[1, 1] = 2/(top - bottom)
    camera[3, 1] = -(top + bottom)/(top - bottom)
    camera[2, 2] = -2/(far - near)
    camera[3, 2] = -(far + near)/(far - near)
    camera[3, 3] = 1

class Scene(draw.Scene):
    __doc__ = draw.Scene.__doc__ + """
    This Scene supports the following features:

    * *pan*: If enabled, mouse movement will translate the scene instead of rotating it
    * *directional_light*: Add directional lights. The given value indicates the magnitude*direction normal vector.
    * *ambient_light*: Enable trivial ambient lighting. The given value indicates the magnitude of the light (in [0, 1]).
    * *translucency*: Enable order-independent transparency rendering
    * *fxaa*: Enable fast approximate anti-aliasing
    * *ssao*: Enable screen space ambient occlusion
    * *additive_rendering*: Enable additive rendering. This mode is good for visualizing densities projected through the viewing direction. Takes an optional 'invert' argument to invert the additive rendering (i.e., black-on-white instead of white-on-black).
    * *outlines*: Enable cartoony outlines. The given value indicates the width of the outlines (start small, perhaps 1e-5 to 1e-3).
    """

    def __init__(self, *args, canvas_kwargs={}, **kwargs):
        self.camera = np.eye(4, dtype=np.float32)
        self._zoom = 1
        self._pixel_scale = 1
        self._clip_scale = 1
        self._translation = [0, 0, 0]
        self._canvas = None
        super(Scene, self).__init__(*args, **kwargs)
        self._canvas = Canvas(self, **canvas_kwargs)

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
        for feature in list(self._enabled_features):
            self.enable(feature, **self._enabled_features[feature])

    def enable(self, name, **parameters):
        if name == 'directional_light':
            lights = parameters.get('value', DEFAULT_DIRECTIONAL_LIGHTS)
            lights = np.atleast_2d(lights).astype(np.float32)
            for prim in self._primitives:
                prim.diffuseLight = lights

        elif name == 'ambient_light':
            light = parameters.get('value', .25)
            for prim in self._primitives:
                prim.ambientLight = light

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
        return self._canvas.show()

    def render(self):
        """Have vispy redraw this Scene object."""
        self._canvas.update()
