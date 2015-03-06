"""Convert an ElementTree to an objectified API."""


class ElemBase(object):

    def __getattr__(self, name):
        elem = self._elem.find(name)
        if elem is None:
            raise AttributeError('no such child: {}'.format(name))
        return Child(self, elem)

    @property
    def tag(self):
        return self._elem.tag

    @tag.setter
    def tag(self, value):
        self._elem.tag = value

    def get(self, key, default=None):
        return self._elem.get(key, default)

    def set(self, key, value):
        self._elem.set(key, value)

    def keys(self):
        return self._elem.keys()

    def items(self):
        return self._elem.items()


class Child(ElemBase):

    def __init__(self, parent, elem):
        super(ElemBase, self).__init__()
        self._parent = parent
        self._elem = elem

    def __getitem__(self, key):
        elems = self._parent._elem.findall(self.tag)
        if isinstance(key, slice):
            return [Child(self._parent, e) for e in elems[key]]
        return Child(self._parent, elems[key])


class Root(ElemBase):

    def __init__(self, elem):
        super(ElemBase, self).__init__()
        self._elem = elem


# Alias to expose it as function
objectify = Root
