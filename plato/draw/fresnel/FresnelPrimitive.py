import fresnel

DEFAULT_MATERIAL = fresnel.material.Material(solid=0,
                                             color=(0, 0, 0),
                                             primitive_color_mix=1,
                                             roughness=0.3,
                                             specular=0.5,
                                             spec_trans=0,
                                             metal=0)

SOLID_MATERIAL = fresnel.material.Material(solid=1,
                                           color=(0, 0, 0),
                                           primitive_color_mix=1,
                                           roughness=0.3,
                                           specular=0.5,
                                           spec_trans=0,
                                           metal=0)


class FresnelPrimitive(object):
    """A mixin class that defines a default :py:class:`fresnel.material.Material`.
    """

    def __init__(self, *args, **kwargs):
        self._material = kwargs.get('material', DEFAULT_MATERIAL)
        super().__init__(*args, **kwargs)


class FresnelPrimitiveSolid(FresnelPrimitive):
    """A mixin class that defines a solid default :py:class:`fresnel.material.Material`.

    This class is useful for 2D visualizations where 3D lights shouldn't cause
    reflections or shine onto otherwise 2D objects.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('material', SOLID_MATERIAL)
        super().__init__(*args, **kwargs)
