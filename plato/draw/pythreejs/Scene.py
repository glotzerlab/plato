import rowan
import numpy as np
import pythreejs

from ... import draw
from ..Scene import DEFAULT_DIRECTIONAL_LIGHTS

class Scene(draw.Scene):
    def __init__(self, *args, **kwargs):
        self._backend_objects = dict(scene=pythreejs.Scene())
        self._clip_scale = 1

        self.z_offset = kwargs.get('translation', (0, 0, 0))[2]

        size = (40, 30)
        (width, height) = size
        dz = np.linalg.norm(size)*self._clip_scale
        self._backend_objects['camera'] = pythreejs.OrthographicCamera(
            -width/2, width/2, height/2, -height/2, 1, 1 + dz, position=(0, 0, 1))
        self._backend_objects['controls'] = pythreejs.OrbitControls(
            self._backend_objects['camera'], target=(0, 0, 0))
        self._backend_objects['scene'].add(self._backend_objects['camera'])
        self._backend_objects['directional_lights'] = []

        (pixel_width, pixel_height) = (width*10, height*10)
        renderer_kwargs = dict(
            width=pixel_width, height=pixel_height, antialias=True,
            **self._backend_objects)
        renderer_kwargs['controls'] = [renderer_kwargs['controls']]
        self._backend_objects['renderer'] = pythreejs.Renderer(**renderer_kwargs)

        super(Scene, self).__init__(*args, **kwargs)
        self._update_canvas_size()

        # directly re-initialize rotation after camera has been set up
        self.rotation = kwargs.get('rotation', (1, 0, 0, 0))
        self.translation = kwargs.get('translation', (0, 0, 0))

    @property
    def zoom(self):
        return self._backend_objects['camera'].zoom

    @zoom.setter
    def zoom(self, value):
        self._backend_objects['camera'].zoom = value

    @property
    def translation(self):
        controls = self._backend_objects['controls']
        translation = -np.array(controls.target)
        translation = rowan.rotate(self.rotation, translation)
        translation[2] += self.z_offset
        return translation

    @translation.setter
    def translation(self, value):
        controls = self._backend_objects['controls']
        value = np.asarray(value) - (0, 0, self.z_offset)
        value = rowan.rotate(rowan.conjugate(self.rotation), value)
        controls.target = (-value).tolist()
        controls.exec_three_obj_method('update')

    @property
    def rotation(self):
        camera = self._backend_objects['camera']
        norm_out = np.array(camera.position)
        norm_out /= np.linalg.norm(norm_out)
        norm_up = np.array(camera.up)
        norm_up -= np.dot(norm_up, norm_out) * norm_out
        norm_up /= np.linalg.norm(norm_up)
        norm_right = np.cross(norm_up, norm_out)
        rotation_matrix = np.array([norm_right, norm_up, norm_out]).T
        result = rowan.from_matrix(rotation_matrix, require_orthogonal=False)
        result = rowan.conjugate(result)
        return result

    @rotation.setter
    def rotation(self, value):
        camera = self._backend_objects['camera']

        # rotating a scene by q is equivalent to rotating the camera's
        # position and up vector by q*
        conj = rowan.conjugate(value)
        camera_distance = np.linalg.norm(camera.position)

        camera.position = rowan.rotate(conj,
                                       [0, 0, camera_distance]).tolist()
        camera.up = rowan.rotate(conj, [0, 1, 0]).tolist()

        self._backend_objects['controls'].exec_three_obj_method('update')

    @property
    def pixel_scale(self):
        return self._pixel_scale

    @pixel_scale.setter
    def pixel_scale(self, value):
        self._pixel_scale = value
        self._update_canvas_size()
        self._update_camera()

    @property
    def clip_scale(self):
        return self._clip_scale

    @clip_scale.setter
    def clip_scale(self, value):
        self._clip_scale = value
        self._update_camera()

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size[:] = value
        self._update_canvas_size()

    def _update_canvas_size(self):
        (pixel_width, pixel_height) = self.size_pixels
        self._backend_objects['renderer'].width = pixel_width
        self._backend_objects['renderer'].height = pixel_height
        self._update_camera()
        self._backend_objects['controls'].exec_three_obj_method('update')

    def _update_camera(self):
        camera = self._backend_objects['camera']
        (width, height) = self.size.astype(np.float32)

        dz = np.sqrt(np.sum(self.size**2))*self._clip_scale

        conj = rowan.conjugate(self.rotation)

        translation = rowan.rotate(conj, [0, 0, 1 + dz/2])

        camera.left = -width/2
        camera.right = width/2
        camera.top = height/2
        camera.bottom = -height/2
        camera.far = 1 + dz
        camera.up = rowan.rotate(conj, (0, 1, 0)).tolist()
        camera.position = translation.tolist()

    def add_primitive(self, prim):
        self._backend_objects['scene'].add(prim.threejs_primitive)
        super(Scene, self).add_primitive(prim)

    def remove_primitive(self, primitive, strict=True):
        self._backend_objects['scene'].remove(primitive.threejs_primitive)
        super(Scene, self).remove_primitive(primitive, strict)

    def _remove_lights(self):
        for _ in range(len(self._backend_objects['directional_lights'])):
            light = self._backend_objects['directional_lights'].pop()
            self._backend_objects['camera'].remove(light)

    def disable(self, name, strict=True):
        super(Scene, self).disable(name, strict)
        if name == 'directional_light':
            self._remove_lights()

    def enable(self, name, auto_value=None, **parameters):
        super(Scene, self).enable(name, auto_value, **parameters)
        if name == 'ambient_light':
            light = pythreejs.AmbientLight('#ffffff', self.get_feature_config(name)['value'])
            self.disable(name, strict=False)
            self._backend_objects['scene'].add(light)
        elif name == 'directional_light':
            # Remove existing lights
            self._remove_lights()
            # Create new lights
            dz = np.linalg.norm(self.size) * self._clip_scale
            for light_vector in np.atleast_2d(
                    self.get_feature_config(name).get('value', DEFAULT_DIRECTIONAL_LIGHTS)):
                position = (-light_vector * dz).tolist()
                light = pythreejs.DirectionalLight(
                    color='#ffffff', position=position, intensity=np.linalg.norm(light_vector))
                self._backend_objects['directional_lights'].append(light)
                self._backend_objects['camera'].add(light)

    def show(self):
        import IPython.display
        IPython.display.display(
            self._backend_objects['renderer'], display_id=str(id(self)))

    def _ipython_display_(self):
        return self.show()
