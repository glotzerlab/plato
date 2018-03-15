from ... import Scene
import numpy as np

def set_orthographic_projection(camera, left, right, bottom, top, near, far):
    camera[:] = 0
    camera[0, 0] = 2/(right - left)
    camera[3, 0] = -(right + left)/(right - left)
    camera[1, 1] = 2/(top - bottom)
    camera[3, 1] = -(top + bottom)/(top - bottom)
    camera[2, 2] = -2/(far - near)
    camera[3, 2] = -(far + near)/(far - near)
    camera[3, 3] = 1

class Scene(Scene):
    def __init__(self, *args, **kwargs):
        self.camera = np.eye(4, dtype=np.float32)
        self._zoom = 1
        self._pixel_scale = 1
        self._clip_scale = 1
        self._translation = [0, 0, 0]
        super(Scene, self).__init__(*args, **kwargs)

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
            lights = parameters.get('lights', (.25, .5, -1))
            lights = np.atleast_2d(lights).astype(np.float32)
            for prim in self._primitives:
                prim.diffuseLight = lights[0]

        elif name == 'ambient_light':
            light = parameters.get('light', .25)
            for prim in self._primitives:
                prim.ambientLight = light

        super(Scene, self).enable(name, **parameters)

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

        self.camera[[0, 1], [0, 1]] *= self._zoom

        for prim in self._primitives:
            prim.camera = self.camera
