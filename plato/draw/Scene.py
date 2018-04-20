import numpy as np

class Scene:
    """A container to hold and display collections of primitives.

    `Scene` keeps track of global information about a set of things to
    be rendered and handles configuration of optional (possibly
    backend-specific) rendering parameters.

    Global information managed by a `Scene` includes the `size` of the
    viewing window, `translation` and `rotation` applied to the scene
    as a whole, and a `zoom` level.

    Primitives can be added to a scene through the `primitives`
    argument of the constructor or the `add_primitive`
    method. Primitives can be retrieved by iterating over the scene::

      for prim in scene:
          # (do something with prim)

    Optional rendering arguments are enabled as *features*, which are
    name-value pairs identifying a feature by name and any
    configuration of the feature in the value.

    """
    def __init__(self, primitives=[], features={}, size=(40, 30),
                 translation=(0, 0, -50), rotation=(1, 0, 0, 0), zoom=1,
                 pixel_scale=20, **kwargs):
        """Initialize a `Scene` object.

        :param primitives: List of primitives to include in the scene, or a single primitive
        :param features: Dictionary mapping names of features to feature configuration options. Options can be single values (which will be converted to `dict(value=given_value)` or dicts.
        :param size: Width and height, in scene units, of the viewport (before scaling by `zoom`)
        :param translation: (x, y, z) translation to be applied to the scene as a whole after rotating. `x` is to the right, `y` is up, and `z` comes toward you out of the screen.
        :param rotation: (r, x, y, z) rotation quaternion to be applied to the scene as a whole.
        :param zoom: Zoom scaling factor to be applied to the scene.
        :param pixel_scale: Number of pixels per scene unit length.
        """
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
                if 'name' in config:
                    raise ValueError('Feature parameters can\'t be named "name"')

                self.enable(feature, **config)
            except TypeError: # config is not of a mapping type
                self.enable(feature, value=config)

        for name in kwargs:
            setattr(self, name, kwargs[name])

    def __iter__(self):
        for prim in self._primitives:
            yield prim

    @property
    def translation(self):
        """(x, y, z) translation to be applied to the scene as a whole after rotating.

        `x` is to the right, `y` is up, and `z` comes toward you out
        of the screen.
        """
        return self._translation

    @translation.setter
    def translation(self, value):
        self._translation[:] = value
        for prim in self._primitives:
            prim.translation = self._translation

    @property
    def rotation(self):
        """(r, x, y, z) rotation quaternion to be applied to the scene as a whole."""
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation[:] = value
        for prim in self._primitives:
            prim.rotation = self._rotation

        if 'link_rotation' in self._enabled_features:
            for target in self._enabled_features['link_rotation']['targets']:
                for prim in target:
                    prim.rotation = self._rotation

    @property
    def size(self):
        """Width and height, in scene units, of the viewport."""
        return self._size

    @size.setter
    def size(self, value):
        self._size[:] = value

    @property
    def size_pixels(self):
        """Width and height, in pixels, of the viewport."""
        return self.size*self.pixel_scale

    @size_pixels.setter
    def size_pixels(self, value):
        self.size = np.asarray(value, dtype=np.float32)/self.pixel_scale

    def add_primitive(self, primitive):
        """Adds a primitive to the scene."""
        self._primitives.append(primitive)
        primitive.translation = self.translation
        primitive.rotation = self.rotation

    def remove_primitive(self, primitive, strict=True):
        """Removes a primitive from the scene.

        :param primitive: primitive to (attempt to) remove
        :param strict: If True, raise an IndexError if the primitive was not in the scene
        """
        try:
            self._primitives.remove(primitive)
        except ValueError:
            if strict:
                raise

    @property
    def enabled_features(self):
        return set(self._enabled_features)

    def get_feature_config(self, name):
        """Return the configuration dictionary for a given feature.

        If the feature has not been enabled, return None.
        """
        if name in self._enabled_features:
            return self._enabled_features[name]
        else:
            return None

    def enable(self, name, auto_value=None, **parameters):
        """Enable an optional rendering feature.

        :param name: Name of the feature to enable
        :param auto_value: Shortcut for features with single-value configuration. If given as a positional argument, will be given the default configuration name 'value'.
        :param parameters: Keyword arguments specifying additional configuration options for the given feature
        """
        if auto_value is not None:
            parameters['value'] = auto_value

        if name == 'link_rotation':
            targets = parameters.setdefault('targets', [])
            if 'target' in parameters:
                targets.append(parameters['target'])
            if 'value' in parameters:
                targets.append(parameters['value'])

            for target in targets:
                target._rotation = self._rotation

        self._enabled_features[name] = dict(parameters)

    def disable(self, name, strict=True):
        """Disable an optional rendering feature.

        :param name: Name of the feature to disable
        :param strict: if True, raise a KeyError if the feature was not enabled
        """
        if not strict and name not in self._enabled_features:
            return

        if name == 'link_rotation':
            targets = self.get_feature_config('link_rotation')['targets']
            for target in targets:
                target._rotation = target._rotation.copy()

        del self._enabled_features[name]
