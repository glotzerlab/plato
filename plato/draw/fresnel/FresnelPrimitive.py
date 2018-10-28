import fresnel

class FresnelPrimitive:
    def __init__(self, *args, material=None, **kwargs):
        if material is None:
            self._material = fresnel.material.Material(primitive_color_mix=1)
        else:
            self._material = material
