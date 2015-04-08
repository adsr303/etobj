"""Convert an ElementTree to an objectified API."""


import collections
import re


NS_RE = re.compile(r'\{.+\}')


class Element(collections.Sequence):

    def __init__(self, elem, parent=None):
        self._elem = elem
        self._parent = parent

    def __getitem__(self, key):
        if self._parent is None:
            return [self][key]
        elems = self._parent._elem.findall(self.tag)
        if isinstance(key, slice):
            return [Element(e, self._parent) for e in elems[key]]
        return Element(elems[key], self._parent)

    def __len__(self):
        if self._parent is None:
            return 1
        return len(self._parent._elem.findall(self.tag))

    def __getattr__(self, name):
        m = NS_RE.match(self._elem.tag)
        tname = '{}{}'.format(m.group(0), name) if m else name
        elem = self._elem.find(tname)
        if elem is None:
            raise AttributeError('no such child: {}'.format(name))
        return Element(elem, self)

    def __str__(self):
        return self.text

    def __eq__(self, other):
        if other is self:
            return True
        if isinstance(other, Element):
            return self._elem == other._elem
        if isinstance(other, basestring):
            return str(self) == other
        return NotImplemented

    def __ne__(self, other):
        eq = (self == other)
        if eq is NotImplemented:
            return NotImplemented
        return not eq

    @property
    def tag(self):
        return self._elem.tag

    @tag.setter
    def tag(self, value):
        self._elem.tag = value

    @property
    def text(self):
        return self._elem.text or ''

    @text.setter
    def text(self, value):
        self._elem.text = value

    @property
    def tail(self):
        return self._elem.tail

    @tail.setter
    def tail(self, value):
        self._elem.tail = value

    def get(self, key, default=None):
        return self._elem.get(key, default)

    def set(self, key, value):
        self._elem.set(key, value)

    def keys(self):
        return self._elem.keys()

    def items(self):
        return self._elem.items()


# Alias to expose it as function
objectify = Element
