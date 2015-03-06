import unittest
import etobj

import xml.etree.ElementTree as ET


def xml(s):
    return etobj.objectify(ET.XML(s))


class TestObjectify(unittest.TestCase):

    def test_subelem(self):
        ob = xml('<a><b/></a>')
        self.assertEqual('b', ob.b.tag)

    def test_subsubelem(self):
        ob = xml('<a><b><c/></b></a>')
        self.assertEqual('c', ob.b.c.tag)

    def test_root_attr(self):
        ob = xml('<a n="zzz"><b/></a>')
        self.assertEqual('zzz', ob.get('n'))

    def test_subelem_attr(self):
        ob = xml('<a><b n="zzz"/></a>')
        self.assertEqual('zzz', ob.b.get('n'))

    def test_subelem_attr_missing(self):
        ob = xml('<a><b n="zzz"/></a>')
        self.assertIsNone(ob.b.get('p'))

    def test_subelem_missing(self):
        ob = xml('<a><b/></a>')
        with self.assertRaises(AttributeError):
            ob.p

    def test_subsubelem_missing(self):
        ob = xml('<a><b><c/></b></a>')
        with self.assertRaises(AttributeError):
            ob.p

    def test_subelem_index(self):
        ob = xml('<a><b n="1"/><b n="2"/></a>')
        self.assertEqual('b', ob.b.tag)
        self.assertEqual('1', ob.b[0].get('n'))
        self.assertEqual('2', ob.b[1].get('n'))

    def test_subelem_len(self):
        ob = xml('<a><n/><b n="1"/><b n="2"/><n/><n/></a>')
        self.assertEqual(2, len(ob.b))
        self.assertEqual(3, len(ob.n))

    def test_subelem_iter(self):
        ob = xml('<a><b n="1"/><b n="2"/></a>')
        self.assertEqual(['1', '2'], [b.get('n') for b in ob.b])

    def test_root_text(self):
        ob = xml('<a>abc<b/>def</a>')
        self.assertEqual('abc', ob.text)

    def test_subelem_text(self):
        ob = xml('<a>xyz<b>abc</b>def</a>')
        self.assertEqual('abc', ob.b.text)

    def test_subelem_tail(self):
        ob = xml('<a>xyz<b>abc</b>def</a>')
        self.assertEqual('def', ob.b.tail)

    def test_subelem_namespace(self):
        ns = 'http://nowhere.com/'
        ob = xml('<n:a xmlns:n="{}"><n:b/></n:a>'.format(ns))
        self.assertEqual('{%s}b' % ns, ob.b.tag)
