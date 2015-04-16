import unittest
import etobj

import xml.etree.ElementTree as ET


def xml(s, *args, **kwargs):
    return etobj.objectify(ET.XML(s), *args, **kwargs)


class TestObjectify(unittest.TestCase):

    def test_subelem(self):
        ob = xml('<a><b/></a>')
        self.assertEqual('b', ob.b.tag)

    def test_subsubelem(self):
        ob = xml('<a><b><c/></b></a>')
        self.assertEqual('c', ob.b.c.tag)

    def test_subsubelem_reference(self):
        ob = xml('<a><b n="1"/><b n="2"/></a>')
        b = ob.b
        self.assertEqual('b', b.tag)
        self.assertEqual(2, len(b))
        self.assertEqual('2', b[1].get('n'))

    def test_root_attr(self):
        ob = xml('<a n="zzz"><b/></a>')
        self.assertEqual('zzz', ob.get('n'))

    def test_root_len(self):
        ob = xml('<a n="zzz"><b/></a>')
        self.assertEqual(1, len(ob))

    def test_root_index(self):
        ob = xml('<a n="zzz"><b/></a>')
        self.assertEqual(ob, ob[0])
        self.assertEqual(ob, ob[-1])

    def test_root_index_out_of_range(self):
        ob = xml('<a n="zzz"><b/></a>')
        with self.assertRaises(IndexError):
            ob[1]

    def test_root_slice(self):
        ob = xml('<a n="zzz"><b/></a>')
        self.assertEqual([ob], ob[:])
        self.assertEqual([ob], ob[0:1])
        self.assertEqual([ob], ob[-1:])

    def test_root_slice_out_of_range(self):
        ob = xml('<a n="zzz"><b/></a>')
        self.assertEqual([], ob[1:3])

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
            ob.b.p

    def test_custom_attr_error_class(self):
        class DummyError(Exception): pass

        ob = xml('<a><b/></a>', attr_error_class=DummyError)
        with self.assertRaises(DummyError):
            ob.p

    def test_custom_attr_error_class_for_subelem(self):
        class DummyError(Exception): pass

        ob = xml('<a><b/></a>', attr_error_class=DummyError)
        with self.assertRaises(DummyError):
            ob.b.p

    def test_custom_attr_error_class_for_subelems(self):
        class DummyError(Exception): pass

        ob = xml('<a><b/><b/></a>', attr_error_class=DummyError)
        with self.assertRaises(DummyError):
            ob.b[1].p

    def test_subelem_index(self):
        ob = xml('<a><b n="1"/><b n="2"/></a>')
        self.assertEqual('b', ob.b.tag)
        self.assertEqual('1', ob.b[0].get('n'))
        self.assertEqual('2', ob.b[1].get('n'))
        self.assertEqual('2', ob.b[-1].get('n'))

    def test_subelem_index_out_of_range(self):
        ob = xml('<a><b n="1"/><b n="2"/></a>')
        with self.assertRaises(IndexError):
            ob.b[2]

    def test_subelem_len(self):
        ob = xml('<a><n/><b n="1"/><b n="2"/><n/><n/></a>')
        self.assertEqual(2, len(ob.b))
        self.assertEqual(3, len(ob.n))

    def test_subelem_slice(self):
        ob = xml('<a><b n="1"/><b n="2"/><b n="3"/></a>')
        self.assertEqual(['1', '2', '3'], [b.get('n') for b in ob.b[:]])
        self.assertEqual(['2', '3'], [b.get('n') for b in ob.b[1:]])
        self.assertEqual(['1'], [b.get('n') for b in ob.b[:1]])

    def test_subelem_slice_out_of_range(self):
        ob = xml('<a><b n="1"/><b n="2"/><b n="3"/></a>')
        self.assertEqual([], ob.b[3:5])

    def test_subelem_iter(self):
        ob = xml('<a><b n="1"/><b n="2"/></a>')
        self.assertEqual(['1', '2'], [b.get('n') for b in ob.b])

    def test_root_text(self):
        ob = xml('<a>abc<b/>def</a>')
        self.assertEqual('abc', ob.text)

    def test_root_str(self):
        ob = xml('<a>abc<b/>def</a>')
        self.assertEqual('abc', str(ob))

    def test_root_eq_str(self):
        ob = xml('<a>abc<b/>def</a>')
        self.assertEqual(ob, 'abc')
        self.assertEqual('abc', ob)

    def test_root_ne_str(self):
        ob = xml('<a>abc<b/>def</a>')
        self.assertNotEqual(ob, 'xyz')
        self.assertNotEqual('xyz', ob)

    def test_root_eq_elem(self):
        ob = xml('<a>abc<b/>def</a>')
        self.assertEqual(ob, ob)

    def test_root_ne_elem(self):
        ob1 = xml('<a>abc<b/>def</a>')
        ob2 = xml('<a>abc<b/>def</a>')
        self.assertNotEqual(ob1, ob2)

    def test_subelem_text(self):
        ob = xml('<a>xyz<b>abc</b>def</a>')
        self.assertEqual('abc', ob.b.text)

    def test_subelem_no_text(self):
        ob = xml('<a><b/></a>')
        self.assertIsNone(ob.b.text)

    def test_subelem_str(self):
        ob = xml('<a>xyz<b>abc</b>def</a>')
        self.assertEqual('abc', str(ob.b))

    def test_subelem_str_no_text(self):
        ob = xml('<a><b/></a>')
        self.assertEqual('', str(ob.b))

    def test_subelem_eq_str(self):
        ob = xml('<a>xyz<b>abc</b>def</a>')
        self.assertEqual(ob.b, 'abc')
        self.assertEqual('abc', ob.b)

    def test_subelem_ne_str(self):
        ob = xml('<a>xyz<b>abc</b>def</a>')
        self.assertNotEqual(ob.b, 'xyz')
        self.assertNotEqual('xyz', ob.b)

    def test_subelem_eq_elem(self):
        ob = xml('<a>xyz<b>abc</b>def</a>')
        self.assertEqual(ob.b, ob.b[0])

    def test_subelem_ne_elem(self):
        ob = xml('<a>xyz<b>abc</b><b>abc</b>def</a>')
        self.assertNotEqual(ob.b, ob.b[1])
        self.assertNotEqual(ob.b[0], ob.b[1])

    def test_subelem_eq_not_implemented(self):
        ob = xml('<a>xyz<b>1</b>def</a>')
        x = 1
        self.assertNotEqual(ob.b, x)
        self.assertNotEqual(x, ob.b)

    def test_subelem_tail(self):
        ob = xml('<a>xyz<b>abc</b>def</a>')
        self.assertEqual('def', ob.b.tail)

    def test_subelem_no_tail(self):
        ob = xml('<a><b>abc</b></a>')
        self.assertIsNone(ob.b.tail)

    def test_subelem_namespace(self):
        ns = 'http://nowhere.com/'
        ob = xml('<n:a xmlns:n="{}"><n:b/></n:a>'.format(ns))
        self.assertEqual('{%s}b' % ns, ob.b.tag)

    def test_subelem_namespace_index(self):
        ns = 'http://nowhere.com/'
        ob = xml('<a xmlns="{}"><b p="1"/><b p="2"/></a>'.format(ns))
        self.assertEqual('1', ob.b[0].get('p'))
        self.assertEqual('2', ob.b[1].get('p'))

    def test_subelem_namespace_iter(self):
        ns = 'http://nowhere.com/'
        ob = xml('<a xmlns="{}"><b p="1"/><b p="2"/></a>'.format(ns))
        self.assertEqual(['1', '2'], [b.get('p') for b in ob.b])

    def test_attrib(self):
        ob = xml('<a m="yyy" n="zzz"></a>')
        self.assertEqual(dict(m='yyy', n='zzz'), ob.attrib)
