import bpy
import numpy as np

from ... import draw

class Scene(draw.Scene):
    __doc__ = draw.Scene.__doc__

    RENDER_COUNT = 0

    def render(self):
        new_scene = bpy.data.scenes.new('plato_{}'.format(self.RENDER_COUNT))
        (width, height) = self.size_pixels
        new_scene.render.resolution_x = width
        new_scene.render.resolution_y = height
        new_scene.render.alpha_mode = 'TRANSPARENT'

        kwargs = dict(scene=new_scene, translation=self.translation,
                      rotation=self.rotation)

        self.render_camera(**kwargs)
        self.render_lights(**kwargs)

        for (i, prim) in enumerate(self._primitives):
            prim.render(suffix=str(i), **kwargs)

        self.RENDER_COUNT += 1
        return new_scene

    def render_camera(self, scene, rotation=(1, 0, 0, 0), **kwargs):
        dz = np.sqrt(np.sum(self.size**2))
        rotation = np.asarray(rotation)

        camera_params = bpy.data.cameras.new('plato_camera')
        camera_params.type = 'ORTHO'
        camera_params.ortho_scale = np.max(self.size/self.zoom)
        camera_object = bpy.data.objects.new('plato_camera', object_data=camera_params)
        camera_object.location = (0, 0, dz)
        scene.objects.link(camera_object)
        scene.camera = camera_object

    def render_lights(self, scene, **kwargs):
        if 'ambient_light' in self.enabled_features:
            pass

        if 'directional_light' in self.enabled_features:
            config = self.get_feature_config('directional_light')
            lights = config.get('value', (.25, .5, -1))
            lights = np.atleast_2d(lights).astype(np.float32)

            for (i, light) in enumerate(lights):
                name = 'light_{}'.format(i)

                magnitude = np.linalg.norm(light)
                direction = light/magnitude

                light_params = bpy.data.lamps.new(name=name, type='SUN')
                light_params.color = (magnitude, magnitude, magnitude)
                light_object = bpy.data.objects.new(name, object_data=light_params)
                scene.objects.link(light_object)

    def show(self):
        blender_scene = self.render()
        bpy.context.screen.scene = blender_scene
        return blender_scene

    def save(self, filename):
        blender_scene = self.show()
        if filename.endswith('.png'):
            blender_scene.render.filepath = filename
            bpy.ops.render.render('INVOKE_DEFAULT', write_still=True)
        else:
            bpy.ops.wm.save_as_mainfile(filepath=filename)
        return blender_scene
