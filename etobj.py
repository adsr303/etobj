"""Convert an ElementTree to an objectified API."""


import collections
import re
import itertools


NS_RE = re.compile(r'\{.+\}')


class Element(collections.Sequence):

    def __init__(self, elem, parent=None, attr_error_class=None):
        # Use __dict__ directly to avoid calls to __setattr__.
        self.__dict__['_elem'] = elem
        self.__dict__['_parent'] = parent
        if attr_error_class is not None:
            self.__dict__['_attr_error_class'] = attr_error_class
        elif parent is not None:
            self.__dict__['_attr_error_class'] = parent._attr_error_class
        else:
            self.__dict__['_attr_error_class'] = AttributeError

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
        return Element(_find(self, name), self)

    def __setattr__(self, name, value):
        # Consider an attribute listed by dir() as 'well-known'. Only setting
        # an 'unknown' attribute should result in creating a subelement.
        if name in dir(self):
            super(Element, self).__setattr__(name, value)
        else:
            if isinstance(value, type(self._elem)):
                new = value
            elif isinstance(value, Element):
                new = value._elem
            else:
                new = _rawelement(self, name, text=value)
            if new.tag != name:
                new.tag = name
            try:
                current = _find(self, name)
            except self._attr_error_class as e:
                self._elem.append(new)
            else:
                idx = list(self._elem).index(current)
                self._elem[idx] = new

    def __delattr__(self, name):
        if name in dir(self):
            super(Element, self).__delattr__(name)
        else:
            elem = _find(self, name)
            self._elem.remove(elem)

    def __str__(self):
        return self.text or ''

    def __eq__(self, other):
        if other is self:
            return True
        if isinstance(other, Element):
            return _equal(self._elem, other._elem)
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
        return self._elem.text

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

    @property
    def attrib(self):
        return self._elem.attrib

    @property
    def elem(self):
        return self._elem

    @property
    def parent(self):
        return self._parent



def root(obj):
    while obj.parent is not None:
        obj = obj.parent
    return obj

def iterancestors(obj):
    anc = obj.parent
    while anc is not None:
        yield anc
        anc = anc.parent

def shallow_signature(obj):
    return _shallow_signature(obj._elem)

def deep_signature(obj):
    return _deep_signature(obj._elem)

# Alias to expose it as function
objectify = Element



def _shallow_signature(elem):
    return (elem.tag, elem.attrib, elem.text, [], elem.tail)

def _deep_signature(elem):
    children = [_deep_signature(c) for c in list(elem)]
    return (elem.tag, elem.attrib, elem.text, children, elem.tail)

def _equal(elem1, elem2):
    if _shallow_signature(elem1) != _shallow_signature(elem2):
        return False
    if len(elem1) != len(elem2):
        return False
    return all(
        _equal(x, y) for x, y in itertools.izip(list(elem1), list(elem2)))

def _rawelement(obj, tag, text):
        new = obj._elem.makeelement(tag, {})
        new.text = text
        return new

def _find(obj, name):
    m = NS_RE.match(obj._elem.tag)
    tname = '{}{}'.format(m.group(0), name) if m else name
    elem = obj._elem.find(tname)
    if elem is None:
        raise obj._attr_error_class('no such child: {}'.format(name))
    return elem
