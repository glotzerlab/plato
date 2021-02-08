import fresnel


def _get_default_material(solid=0):
    """Return a default material type.

    2D shapes should use ``solid=1`` to remove lighting effects.
    """
    return fresnel.material.Material(
        solid=solid,
        color=(0, 0, 0),
        primitive_color_mix=1,
        roughness=0.3,
        specular=0.5,
        spec_trans=0,
        metal=0,
    )


class FresnelPrimitive(object):
    """A mixin class that defines a default :py:class:`fresnel.material.Material`."""

    def __init__(self, *args, **kwargs):
        self._material = kwargs.get("material", _get_default_material(solid=0))
        super().__init__(*args, **kwargs)


class FresnelPrimitiveSolid(FresnelPrimitive):
    """A mixin class that defines a solid default :py:class:`fresnel.material.Material`.

    This class is useful for 2D visualizations where 3D lights shouldn't cause
    reflections or shine onto otherwise 2D objects.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("material", _get_default_material(solid=1))
        super().__init__(*args, **kwargs)
