import multiprocessing
import os
import subprocess
import tempfile

from ... import draw
from ... import math
import numpy as np

class Scene(draw.Scene):
    __doc__ = draw.Scene.__doc__ + """
    This Scene supports the following features:

    * *antialiasing*: Enable antialiasing using the given value (default 0.3).
    * *ambient_light*: Enable trivial ambient lighting. The given value indicates the magnitude of the light (in [0, 1]).
    * *directional_light*: Add directional lights. The given value indicates the magnitude*direction normal vector.
    * *multithreading*: Enable multithreaded rendering. The given value indicates the number of threads to use.
    """

    def render(self):
        """Render all the shapes in this scene.

        :returns: povray string representing the entire scene
        """
        lines = []

        background = (1, 1, 1)
        lines.append('background {{color rgb <{},{},{}>}}'.format(*background))

        lines.extend(self.render_camera())

        lines.extend(self.render_lights())

        shapeIndex = 0
        for i, prim in enumerate(self._primitives):
            lines.extend(prim.render(
                translation=self.translation, rotation=self.rotation,
                name_suffix=i))

        return '\n'.join(lines)

    def render_camera(self):
        (width, height) = self.size/self.zoom
        dz = np.sqrt(np.sum(width**2 + height**2))

        camera = ('camera {{ orthographic location <0, 0, {dz}> up <0, {height}, 0> '
                  'right <{width}, 0, 0> look_at <0, 0, 0> }}').format(
                      dz=dz, height=height, width=-width)
        return [camera]

    def render_lights(self):
        result = []

        if 'ambient_light' in self._enabled_features:
            config = self._enabled_features['ambient_light']

            (width, height) = self.size/self.zoom
            dz = np.sqrt(np.sum(width**2 + height**2))

            pos = (0, 0, 2*dz)
            basis0 = (4*dz, 0, 0)
            basis1 = (0, 4*dz, 0)

            light = ('light_source {{ <{pos[0]}, {pos[1]}, {pos[2]}> color '
                     'rgb<{mag}, {mag}, {mag}> '
                     'area_light <{basis0[0]}, {basis0[1]}, {basis0[2]}>, '
                     '<{basis1[0]}, {basis1[1]}, {basis1[2]}>, 5, 5 '
                     'adaptive 1 jitter shadowless }}').format(
                         pos=pos, mag=config.get('value', 0.25),
                         basis0=basis0, basis1=basis1)
            result.append(light)

        if 'directional_light' in self._enabled_features:
            config = self._enabled_features['directional_light']
            lights = config.get('value', (.25, .5, -1))
            lights = np.atleast_2d(lights).astype(np.float32)

            dz = np.sqrt(np.sum((self.size/self.zoom)**2))
            for direction in lights:
                magnitude = np.linalg.norm(direction)
                norm = direction/magnitude
                position = -norm*dz*2

                # we want to rotate the basis vectors, constructed to
                # be at (0, 0, dz), to be perpendicular to the given
                # direction
                halftheta = np.arccos(norm[2])/2
                cross = np.cross([0, 0, 1], norm)
                cross /= np.linalg.norm(cross)
                quat = np.array([np.cos(halftheta)] + (np.sin(halftheta)*cross).tolist())

                basis0 = np.array([dz, 0, 0])
                basis0 = math.quatrot(quat, basis0)
                basis1 = np.array([0, dz, 0])
                basis1 = math.quatrot(quat, basis1)

                light = ('light_source {{ <{pos[0]}, {pos[1]}, {pos[2]}> color '
                         'rgb<{mag}, {mag}, {mag}> '
                         'area_light <{basis0[0]}, {basis0[1]}, {basis0[2]}>, '
                         '<{basis1[0]}, {basis1[1]}, {basis1[2]}>, 5, 5 '
                         'adaptive 1 jitter }}').format(
                             pos=position, mag=magnitude, basis0=basis0, basis1=basis1)
                result.append(light)

        return result

    def show(self):
        """Render the scene to an image and display using ipython."""
        import IPython.display

        with tempfile.NamedTemporaryFile(suffix='.png') as temp:
            self.save(temp.name)
            return IPython.display.Image(filename=temp.name)

    def save(self, filename):
        """Save the scene, either as povray source or a rendered image.

        :param filename: target filename to save the result into. If filename ends in .pov, save the povray source, otherwise call povray to render the image
        """
        (width, height) = self.size_pixels
        povstring = self.render()

        if 'antialiasing' in self._enabled_features:
            antialiasing = self._enabled_features['antialiasing'].get('value', .3)
        else:
            antialiasing=None

        if 'multithreading' in self._enabled_features:
            threads = self._enabled_features['multithreading'].get(
                'value', multiprocessing.cpu_count())
        else:
            threads = None

        return self.call_povray(
            povstring, filename, width, height, antialiasing, threads)

    @staticmethod
    def call_povray(contents, filename, width, height, antialiasing=None, threads=None):
        povfile = filename + '.pov'
        with open(povfile, 'w') as f:
            f.write(contents)

        command = ['povray', '+I{}'.format(povfile), '+O{}'.format(filename),
                   '+W{}'.format(width), '+H{}'.format(height)]

        if antialiasing:
            command.append('+A{}'.format(antialiasing))

        if threads:
            command.append('+WT{}'.format(threads))

        try:
            return subprocess.check_call(command)
        finally:
            os.remove(povfile)
