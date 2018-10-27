import fresnel
import numpy as np
import rowan
from ... import draw


class Scene(draw.Scene):
    __doc__ = draw.Scene.__doc__ + """
    This Scene supports the following features:

    * *antialiasing*: Enable antialiasing, for the preview tracer only. This uses fresnel's aa_level=3 if set, 0 otherwise.
    * *pathtracer*: Enable the path tracer. Accepts parameter ``samples`` with default value 64.
    * *outlines*: Enable cartoony outlines. The given value indicates the width of the outlines (start small, perhaps 1e-5 to 1e-3).
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
        if self._output is None:
            self.render()
        return self._output

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
        self._fresnel_scene.camera = fresnel.camera.orthographic(
            position=camera_position,
            look_at=camera_look_at,
            up=camera_up,
            height=camera_height)

        if 'pathtracer' in self._enabled_features:
            # Use path tracer if enabled
            config = self._enabled_features.get('pathtracer', {})
            tracer = self._path_tracer
            samples = config.get('samples', 64)
            def render_function(scene, **kwargs):
                return tracer.sample(scene, samples, **kwargs)
        else:
            # Use preview tracer by default
            tracer = self._preview_tracer
            tracer.aa_level = 3 if 'antialiasing' in self._enabled_features else 0
            render_function = tracer.render

        self._output = render_function(self._fresnel_scene)
