"""Convert an ElementTree to an objectified API."""


import collections
import re
import itertools


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
        elems = _siblings(self)
        if isinstance(key, slice):
            return [Element(e, self.parent) for e in elems[key]]
        return Element(elems[key], self.parent)

    def __len__(self):
        return len(_siblings(self))

    def __getattr__(self, name):
        return Element(_find(self, name), self)

    def __setattr__(self, name, value):
        # Consider an attribute listed by dir() as 'well-known'. Only setting
        # an 'unknown' attribute should result in creating a subelement.
        if name in dir(self):
            super(Element, self).__setattr__(name, value)
        else:
            if isinstance(value, type(self.elem)):
                new = value
            elif isinstance(value, Element):
                new = value.elem
            else:
                new = _newelem(self, name, text=value)
            if new.tag != name:
                new.tag = name
            try:
                current = _find(self, name)
            except self._attr_error_class as e:
                self.elem.append(new)
            else:
                idx = list(self.elem).index(current)
                self.elem[idx] = new

    def __delattr__(self, name):
        if name in dir(self):
            super(Element, self).__delattr__(name)
        else:
            elem = _find(self, name)
            self.elem.remove(elem)

    def __str__(self):
        return self.text or ''

    def __eq__(self, other):
        if other is self:
            return True
        if isinstance(other, Element):
            return _equal(self.elem, other.elem)
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
        return self.elem.tag

    @tag.setter
    def tag(self, value):
        self.elem.tag = value

    @property
    def text(self):
        return self.elem.text

    @text.setter
    def text(self, value):
        self.elem.text = value

    @property
    def tail(self):
        return self.elem.tail

    @tail.setter
    def tail(self, value):
        self.elem.tail = value

    def get(self, key, default=None):
        return self.elem.get(key, default)

    def set(self, key, value):
        self.elem.set(key, value)

    def keys(self):
        return self.elem.keys()

    def items(self):
        return self.elem.items()

    @property
    def attrib(self):
        return self.elem.attrib

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
    return _shallow_signature(obj.elem)

def deep_signature(obj):
    return _deep_signature(obj.elem)

# Alias to expose it as function
objectify = Element


NS_RE = re.compile(r'\{.+\}')

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

def _newelem(obj, tag, text):
    new = obj.elem.makeelement(tag, {})
    new.text = text
    return new

def _find(obj, name):
    m = NS_RE.match(obj.elem.tag)
    tname = '{}{}'.format(m.group(0), name) if m else name
    elem = obj.elem.find(tname)
    if elem is None:
        raise obj._attr_error_class('no such child: {}'.format(name))
    return elem

def _siblings(obj):
    if obj.parent is None:
        return [obj.elem]
    return obj.parent.elem.findall(obj.tag)
