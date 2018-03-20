import numpy as np
import vispy, vispy.app
import vispy.gloo as gloo

class Canvas(vispy.app.Canvas):
    def __init__(self, scene):
        super(Canvas, self).__init__(size=scene.size_pixels.astype(np.uint32))

        gloo.set_viewport(0, 0, *scene.size_pixels.astype(np.uint32))

        self._scene = scene
        self._mouse_origin = np.array([0, 0], dtype=np.float32)
        self._selection_callback = None

    def on_draw(self, *args, **kwargs):
        self.set_current()
        vispy.gloo.set_state(preset='opaque',
                             depth_test=True,
                             blend=False,
                             depth_mask=True)

        gloo.clear((1, 1, 1, 1), depth=True)
        for prim in self._scene._primitives:
            prim.render_color()

    def on_mouse_press(self, event):
        self._mouse_origin[:] = event.pos

    def on_mouse_release(self, event):
        if self._selection_callback is not None:
            callback = self._selection_callback
            self._selection_callback = None
            callback(self._mouse_origin, event.pos)

    def on_key_press(self, event):
        if event.key == 'X' or event.key == 'Y' or event.key == 'Z':
            self._mouse_origin = np.array([0, 0], dtype=np.float32)
            self._scene.translation = (0, 0, 0)
            self.update()

    def _mouse_translate(self, delta):
        scale = 2/np.array(self._scene.size_pixels)/self._scene.camera[[0, 1], [0, 1]]*[1, -1]
        translation = self._scene.translation
        translation[:2] += scale*delta
        self._scene.translation = translation
        self.update()

    def on_mouse_wheel(self, event):
        self._scene.zoom *= 1.1**event.delta[1]
        self.update()

    def on_mouse_move(self, event):
        if event.handled or self._selection_callback is not None:
            return

        if 1 in event.buttons or 2 in event.buttons:
            delta = (event.pos - self._mouse_origin)/np.sqrt(np.product(self._scene.size_pixels))
            self._mouse_origin[:] = event.pos
            if 'control' in event.modifiers or 'meta' in event.modifiers:
                self.planeRotation(event, delta)
            elif 'alt' in event.modifiers or 'pan' in self._scene._enabled_features:
                # undo the mean size scaling we applied above
                self._mouse_translate(delta*np.sqrt(np.product(self._scene.size_pixels)))
            else:
                self.updateRotation(event, delta)

    def on_key_press(self, event):
        if event.key == 'Right' and (
                'control' in event.modifiers or 'meta' in event.modifiers):
            self.updateRotation(event, delta=(np.pi/36,0))
        elif event.key == 'Left' and (
                'control' in event.modifiers or 'meta' in event.modifiers):
            self.updateRotation(event, delta=(-np.pi/36,0))
        elif event.key == 'Up' and (
                'control' in event.modifiers or 'meta' in event.modifiers):
            self.updateRotation(event, delta=(0,-np.pi/36))
        elif event.key == 'Down' and (
                'control' in event.modifiers or 'meta' in event.modifiers):
            self.updateRotation(event, delta=(0,np.pi/36))
        elif event.key == 'X' or event.key == 'Y' or event.key == 'Z':
            self._scene.rotation = np.asarray([1., 0., 0., 0.], dtype=np.float32)
            if event.key == 'Y':
                self.updateRotation(event, delta=(0,-np.pi/6), suppress=True)
            elif event.key == 'Z':
                self.updateRotation(event, delta=(-np.pi/6, 0), suppress=True)
        self.update()


    def planeRotation(self, event, delta=(0,0)):
        delta = np.asarray(delta, dtype=np.float32)
        theta = -delta[0] * (0.1 if 'shift' in event.modifiers else 1)
        updated = False

        if np.absolute(theta) > 1e-5:
            theta *= (3.0 if 'shift' not in event.modifiers else 1)
            quat = np.array([np.cos(theta/2), 0, 0, np.sin(theta/2)])
            real = (self._scene.rotation[0]*quat[0] - np.dot(self._scene.rotation[1:], quat[1:]))
            imag = (self._scene.rotation[0]*quat[1:] + quat[0]*self._scene.rotation[1:] + np.cross(quat[1:], self._scene.rotation[1:]))
            self._scene.rotation = [real] + imag.tolist()
            updated = True

        if np.absolute(delta[1]) > 1e-5:
            amount = -delta[1]*(1. if 'shift' in event.modifiers else 20.)
            self._scene.zoom *= 1.1**amount
            updated = True

        if updated:
            self.update()

    def updateRotation(self, event, delta=(0,0), suppress=False):
        delta = np.asarray(delta, dtype=np.float32)[::-1]
        theta = np.sqrt(np.sum(delta**2)) * (0.1 if (not suppress)
                                                  and ('shift' in event.modifiers)
                                                  else 1)

        if np.absolute(theta) > 1e-5:
            norm = delta/(theta * (10 if (not suppress) and ('shift' in event.modifiers) else 1))
            theta *= (3.0 if (suppress) or ('shift' not in event.modifiers) else 1)
            quat = np.array([np.cos(theta/2),
                             np.sin(theta/2)*norm[0],
                             np.sin(theta/2)*norm[1], 0])
            real = (self._scene.rotation[0]*quat[0] - np.dot(self._scene.rotation[1:], quat[1:]))
            imag = (self._scene.rotation[0]*quat[1:] + quat[0]*self._scene.rotation[1:] + np.cross(quat[1:], self._scene.rotation[1:]))
            self._scene.rotation = [real] + imag.tolist()
            self.update()
