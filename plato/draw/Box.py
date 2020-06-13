import functools
import itertools

import numpy as np

from .. import math
from .internal import ShapeDecorator, ShapeAttribute
from .Lines import Lines

@ShapeDecorator
class Box(Lines):
    """A triclinic box frame.

    This primitive draws a triclinic box centered at the origin. It is
    specified in terms of three lattice vector lengths `Lx`, `Ly`,
    `Lz` and tilt factors, defined using the `hoomd-blue schema
    <https://hoomd-blue.readthedocs.io/en/stable/box.html>`_.

    Rather than directly initializing via attributes, `Box` objects
    can also be automatically created from box-type objects using the
    :py:func:`from_box` method.

    Examples::

        Lx = Ly = Lz = 10
        xy = xz = yz = 0
        box_primitive = draw.Box(Lx=Lx, Ly=Ly, Lz=Lz, width=width, color=color)
        box_tuple = (Lx, Ly, Lz, xy, xz, yz)
        box_primitive = draw.Box.from_box(box_tuple)

    """

    _ATTRIBUTES = Lines._ATTRIBUTES + list(
        itertools.starmap(ShapeAttribute, [
            ('Lx', np.float32, 1, 0, False,
             'Length of first box vector'),
            ('Ly', np.float32, 1, 0, False,
             'Length of second box vector'),
            ('Lz', np.float32, 1, 0, False,
             'Length of third box vector'),
            ('xy', np.float32, 0, 0, False,
             'Tilt factor between the first and second box vectors'),
            ('xz', np.float32, 0, 0, False,
             'Tilt factor between the first and third box vectors'),
            ('yz', np.float32, 0, 0, False,
             'Tilt factor between the second and third box vectors'),
            ('width', np.float32, 0.01, 0, False,
             'Width of box line segments'),
            ('color', np.float32, (0, 0, 0, 1), 1, False,
             'Color, RGBA, [0, 1] for the box line segments'),
        ]))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # specially set these attributes since the array-broadcasting
        # behavior depends on calling the property setter
        if 'width' not in kwargs:
            self.width = 0.01
        if 'color' not in kwargs:
            self.color = (0, 0, 0, 1)
        # ...and set this one because it's non-default
        if 'cap_mode' not in kwargs:
            self.cap_mode = 1

    @classmethod
    def from_box(cls, box, width=0.01, color=(0, 0, 0, 1)):
        """Duck type the box from a valid input.

        Boxes can be a list, dictionary, or object with attributes.
        """
        try:
            # Handles freud.box.Box and namedtuple
            Lx = box.Lx
            Ly = box.Ly
            Lz = getattr(box, 'Lz', 0)
            xy = getattr(box, 'xy', 0)
            xz = getattr(box, 'xz', 0)
            yz = getattr(box, 'yz', 0)
        except AttributeError:
            try:
                # Handle dictionary-like
                Lx = box['Lx']
                Ly = box['Ly']
                Lz = box.get('Lz', 0)
                xy = box.get('xy', 0)
                xz = box.get('xz', 0)
                yz = box.get('yz', 0)
            except (IndexError, KeyError, TypeError):
                if not len(box) in [2, 3, 6]:
                    raise ValueError(
                        "List-like objects must have length 2, 3, or 6 to be "
                        "converted to a box.")
                # Handle list-like
                Lx = box[0]
                Ly = box[1]
                Lz = box[2] if len(box) > 2 else 0
                xy, xz, yz = box[3:6] if len(box) == 6 else (0, 0, 0)
        return cls(Lx=Lx, Ly=Ly, Lz=Lz, xy=xy, xz=xz, yz=yz, width=width, color=color)

    def _update_coordinates(self, *args, **kwargs):
        box_tuple = (self.Lx, self.Ly, self.Lz, self.xy, self.xz, self.yz)

        fractions = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1],
                              [1, 1, 0], [1, 0, 1], [0, 1, 1], [1, 1, 1]])
        coordinates = math.fractions_to_coordinates(box_tuple, fractions)
        start_points = coordinates[[0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 5, 6]]
        end_points = coordinates[[1, 2, 3, 4, 5, 4, 6, 5, 6, 7, 7, 7]]

        self.start_points = start_points
        self.end_points = end_points

    Lx = Ly = Lz = xy = xz = yz = _update_coordinates

    @property
    def width(self):
        return self.widths[0]

    @width.setter
    def width(self, value):
        self.widths = np.repeat(value, 12)

    @property
    def color(self):
        return self.colors[0]

    @color.setter
    def color(self, value):
        self.colors = np.tile(np.atleast_2d(value), (12, 1))
