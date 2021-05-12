import fresnel
import numpy as np
import rowan

from ... import draw

class Scene(draw.Scene):
    __doc__ = (draw.Scene.__doc__ or '') + """
    This Scene supports the following features:

    * *antialiasing*: Enable antialiasing, for the preview tracer only.
    * *pathtracer*: Enable the path tracer. Accepts parameter ``samples`` with default value 64.
    * *directional_light*: Add directional lights. The given vector(s) indicates the light direction. The length of the vector(s) determines the magnitude of the light(s).
    * *ambient_light*: Enable ambient lighting. The given value indicates the magnitude of the light.
    """

    def __init__(self, *args, tracer_kwargs={}, **kwargs):
        super(Scene, self).__init__(*args, **kwargs)
        self._device = fresnel.Device()
        self._fresnel_scene = fresnel.Scene(device=self._device)
        default_size = self.size_pixels.astype(np.uint32)
        self._preview_tracer = fresnel.tracer.Preview(
            device=self._device, w=default_size[0], h=default_size[1])
        self._path_tracer = fresnel.tracer.Path(
            device=self._device, w=default_size[0], h=default_size[1])
        self._geometries = []
        self._output = None

    def show(self):
        """Render the scene to an image and display using IPython."""
        import IPython
        if self._output is None:
            self.render()
        IPython.display.display(self._output, display_id=str(id(self)))

    def save(self, filename):
        """Render and save an image of this Scene.

        :param filename: target filename to save the image into
        """
        try:
            import PIL
        except ImportError:
            raise RuntimeError('Could not import PIL. PIL (pillow) is required to save fresnel images.')
        else:
            if self._output is None:
                self.render()
            image = PIL.Image.fromarray(self._output[:], mode='RGBA')
            image.save(filename)

    def render(self):
        """Render this Scene object."""
        # Remove existing fresnel geometries from the scene
        for geometry in self._geometries:
            geometry.remove()

        # Clear the list of fresnel geometries
        self._geometries = []

        # Add fresnel scene geometries from plato scene primitives
        for prim in self._primitives:
            geometry = prim.render(self._fresnel_scene)
            self._geometries.append(geometry)

        # Set up the camera
        camera_up = rowan.rotate(rowan.conjugate(self.rotation), [0, 1, 0])
        camera_position = rowan.rotate(rowan.conjugate(self.rotation), -self.translation)
        camera_look_at = camera_position + rowan.rotate(rowan.conjugate(self.rotation), [0, 0, -1])
        camera_height = self.size[1]/self.zoom
        try:
            orthographic_camera = fresnel.camera.Orthographic
        except AttributeError:
            # Support fresnel < 0.13.0
            orthographic_camera = fresnel.camera.orthographic
        self._fresnel_scene.camera = orthographic_camera(
            position=camera_position,
            look_at=camera_look_at,
            up=camera_up,
            height=camera_height)

        # Set up lights
        lights = []
        if 'ambient_light' in self.enabled_features:
            config = self.get_feature_config('ambient_light')
            magnitude = config.get('value', 0.25)
            if magnitude > 0:
                lights.append(fresnel.light.Light(direction=(0, 0, 1),
                                                  color=(magnitude, magnitude, magnitude),
                                                  theta=np.pi))
        if 'directional_light' in self.enabled_features:
            config = self.get_feature_config('directional_light')
            directions = config.get('value', (.25, .5, -1))
            directions = np.atleast_2d(directions).astype(np.float32)
            for direction in directions:
                magnitude = np.linalg.norm(direction)
                if magnitude > 0:
                    lights.append(fresnel.light.Light(direction=-direction,
                                                      color=(magnitude, magnitude, magnitude),
                                                      theta=0.7))
        if len(lights) > 0:
            self._fresnel_scene.lights = lights

        # Set up tracer
        if 'pathtracer' in self.enabled_features:
            # Use path tracer if enabled
            config = self.get_feature_config('pathtracer')
            tracer = self._path_tracer
            samples = config.get('samples', 64)
            def render_function(scene, **kwargs):
                return tracer.sample(scene, samples, **kwargs)
        else:
            # Use preview tracer by default
            tracer = self._preview_tracer
            tracer.anti_alias = 'antialiasing' in self.enabled_features
            render_function = tracer.render

        self._output = render_function(self._fresnel_scene)

    def _ipython_display_(self):
        return self.show()
