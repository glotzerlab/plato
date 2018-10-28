import fresnel

class FresnelPrimitive:
    def __init__(self, *args, material=None, **kwargs):
        if material is None:
            self._material = fresnel.material.Material(solid=0,
                                                       color=(0, 0, 0),
                                                       primitive_color_mix=1,
                                                       roughness=0.3,
                                                       specular=0.5,
                                                       spec_trans=0,
                                                       metal=0)
        else:
            self._material = material
