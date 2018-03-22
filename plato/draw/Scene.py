import numpy as np

class Scene:
    def __init__(self, primitives=[], features={}, size=(40, 30),
                 translation=(0, 0, -50), rotation=(1, 0, 0, 0), zoom=1,
                 pixel_scale=20, **kwargs):
        # map each enabled feature's name to a configuration object
        self._enabled_features = dict()

        try:
            self._primitives = list(primitives)
        except TypeError:
            self._primitives = [primitives]

        self._size = np.ones((2,), dtype=np.float32)
        self.pixel_scale = pixel_scale
        self.size = size
        self.zoom = zoom

        self._translation = np.zeros((3,), dtype=np.float32)
        self.translation = translation
        self._rotation = np.array([1, 0, 0, 0], dtype=np.float32)
        self.rotation = rotation

        for feature in features:
            config = features[feature]
            try:
                self.enable(feature, **config)
            except TypeError: # config is not of a mapping type
                self.enable(feature, value=config)

        for name in kwargs:
            setattr(self, name, kwargs[name])

    @property
    def translation(self):
        return self._translation

    @translation.setter
    def translation(self, value):
        self._translation[:] = value
        for prim in self._primitives:
            prim.translation = self._translation

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation[:] = value
        for prim in self._primitives:
            prim.rotation = self._rotation

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size[:] = value

    @property
    def size_pixels(self):
        return self.size*self.pixel_scale

    @size_pixels.setter
    def size_pixels(self, value):
        self.size = value/self.pixel_scale

    def add_primitive(self, primitive):
        self._primitives.append(primitive)

    def remove_primitive(self, primitive, strict=True):
        try:
            self._primitives.remove(primitive)
        except IndexError:
            if strict:
                raise

    def enable(self, name, auto_value=None, **parameters):
        if auto_value is not None:
            parameters['value'] = auto_value
        self._enabled_features[name] = dict(parameters)

    def disable(self, name, strict=True):
        if not strict and name not in self._enabled_features:
            return

        del self._enabled_features[name]
