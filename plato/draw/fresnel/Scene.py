import fresnel
from ... import draw


class Scene(draw.Scene):
    __doc__ = draw.Scene.__doc__ + """
    This Scene supports the following features:

    * *directional_light*: Add directional lights. The given value indicates the magnitude*direction normal vector.
    * *ambient_light*: Enable trivial ambient lighting. The given value indicates the magnitude of the light (in [0, 1]).
    * *outlines*: Enable cartoony outlines. The given value indicates the width of the outlines (start small, perhaps 1e-5 to 1e-3).
    """

    def __init__(self, *args, tracer_kwargs={}, **kwargs):
        super(Scene, self).__init__(*args, **kwargs)
        self._device = fresnel.Device()
        self._fresnel_scene = fresnel.Scene(device=self._device)
        default_size = [600, 400]
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

    def render(self, *args, tracer='path', **kwargs):
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

        if tracer == 'preview':
            tracer = self._preview_tracer
            if 'aa_level' in kwargs:
                tracer.aa_level = kwargs.pop('aa_level')
            render_function = tracer.render
        elif tracer == 'path':
            tracer = self._path_tracer
            if 'samples' in kwargs:
                samples = kwargs.pop('samples')
            else:
                samples = 64
            def render_function(scene, **kwargs):
                return tracer.sample(scene, samples, **kwargs)
        else:
            raise RuntimeError("Tracer '{}' does not exist.".format(tracer))

        self._output = render_function(self._fresnel_scene, *args, **kwargs)
