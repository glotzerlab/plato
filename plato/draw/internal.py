import functools
import inspect
from collections import namedtuple
import numpy as np

ATTRIBUTE_DOCSTRING_HEADER = '\n\nThis primitive has the following attributes:'
ATTRIBUTE_DOCSTRING_TEMPLATE = '    * {name}: {description}'

def enforce_scalar(value):
    result = np.asarray(value)
    assert result.shape == (), 'Non-scalar value given for a scalar attribute'
    return result

array_size_checkers = [enforce_scalar, np.atleast_1d, np.atleast_2d, np.atleast_3d]

class Shape:
    def __init__(self, **kwargs):
        self._attributes = {}
        self._dirty_attributes = {attr.name for attr in self._ATTRIBUTES}

        for attr in self._ATTRIBUTES:
            size_checker = array_size_checkers[attr.dimension]
            value = size_checker(np.asarray(attr.default, dtype=attr.dtype))
            self._attributes[attr.name] = value

        for name in kwargs:
            setattr(self, name, kwargs[name])

    def __setattr__(self, name, value):
        try:
            if not name.startswith('_') and name not in self._ATTRIBUTES_BY_NAME:
                self._attributes[name] = value
        except AttributeError:
            pass
        super(Shape, self).__setattr__(name, value)

    @classmethod
    def link(cls, other, share_redraw_state=True):
        """Causes this shape to share its data with another shape.

        Common values that are set in `other` will be set in this shape.

        :param other: Other shape to link this one to
        :param share_redraw_state: If True, share the redrawing state (for dynamic visualization backends) with `other`
        """
        # use copy() in case ctor needs some non-default arguments
        # (should be cheap since we are just shuffling pointers anyway
        # for large array data)
        result = cls.copy(other)
        result._attributes = other._attributes
        if share_redraw_state:
            result._dirty_attributes = other._dirty_attributes
        return result

    @classmethod
    def copy(cls, other):
        """Create a copy of another shape."""
        result = cls(**other._attributes)
        return result

def attribute_setter(self, value, name, dtype, dimension, default):
    size_checker = array_size_checkers[dimension]
    result = size_checker(np.asarray(value, dtype=dtype))
    assert default.ndim == 0 or result.shape[-default.ndim:] == self._ATTRIBUTE_DIMENSIONS[name], 'Invalid shape for property {}: {}'.format(name, result.shape)
    self._dirty_attributes.add(name)
    self._attributes[name] = result

def attribute_getter(self, name):
    return self._attributes[name]

def ShapeDecorator(cls):
    cls._ATTRIBUTE_DIMENSIONS = {}
    cls._ATTRIBUTES_BY_NAME = {}
    attribute_doc_lines = [ATTRIBUTE_DOCSTRING_HEADER]

    for attr in cls._ATTRIBUTES:
        array_default = np.array(attr.default)
        cls._ATTRIBUTE_DIMENSIONS[attr.name] = array_default.shape
        cls._ATTRIBUTES_BY_NAME[attr.name] = attr

        attribute_doc_lines.append(ATTRIBUTE_DOCSTRING_TEMPLATE.format(
            name=attr.name, description=attr.description))

        getter = functools.partial(attribute_getter, name=attr.name)
        setter = functools.partial(
            attribute_setter, name=attr.name, dtype=attr.dtype,
            dimension=attr.dimension, default=array_default)
        prop = property(getter, setter, doc=attr.description)

        setattr(cls, attr.name, prop)

    if cls.__doc__ is None:
        cls.__doc__ = ''

    cls.__doc__ = inspect.cleandoc(cls.__doc__) + '\n'.join(attribute_doc_lines)
    return cls

ShapeAttribute = namedtuple('ShapeAttrib', ['name', 'dtype', 'default', 'dimension', 'description'])
