import unittest
import etobj

import xml.etree.ElementTree as ET


def xml(s, *args, **kwargs):
    return etobj.objectify(ET.XML(s), *args, **kwargs)


class TestBasics(unittest.TestCase):

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


class TestReadingSubelements(unittest.TestCase):

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


class TestModifyingSubelements(unittest.TestCase):

    def test_sets_subelem_no_text(self):
        ob = xml('<a/>')
        ob.b = None
        self.assertEqual(xml('<a><b/></a>'), ob)

    def test_sets_subelem_with_text(self):
        ob = xml('<a/>')
        ob.b = 'foo'
        self.assertEqual(xml('<a><b>foo</b></a>'), ob)

    def test_sets_etree_as_subelem(self):
        ob = xml('<a/>')
        raw_elem = ET.XML('<b><c/></b>')
        ob.b = raw_elem
        self.assertEqual(xml('<a><b><c/></b></a>'), ob)

    def test_coerces_tag_for_etree_subelem(self):
        ob = xml('<a/>')
        raw_elem = ET.XML('<b foo="bar"/>')
        ob.c = raw_elem
        self.assertEqual(xml('<a><c foo="bar"/></a>'), ob)

    def test_sets_other_element_as_subelem(self):
        ob = xml('<a/>')
        other = xml('<b><c/></b>')
        ob.b = other
        self.assertEqual(xml('<a><b><c/></b></a>'), ob)

    def test_coerces_tag_for_other_element_as_subelem(self):
        ob = xml('<a/>')
        other = xml('<b foo="bar"/>')
        ob.c = other
        self.assertEqual(xml('<a><c foo="bar"/></a>'), ob)

    def test_overrides_if_subelem_set_twice(self):
        ob = xml('<a/>')
        ob.b = 'foo'
        ob.b = 'bar'
        self.assertEqual(xml('<a><b>bar</b></a>'), ob)

    def test_overrides_with_various_subelem_types(self):
        ob = xml('<a/>')
        ob.b = 'foo'
        ob.b = ET.XML('<b foo="bar"/>')
        self.assertEqual(xml('<a><b foo="bar"/></a>'), ob)
        ob.b = xml('<c bar="baz"/>')
        self.assertEqual(xml('<a><b bar="baz"/></a>'), ob)

    def test_overrides_exactly_first_child_if_set_again(self):
        ob = xml('<a><x/><b>foo</b><b>bar</b><b>baz</b><y/></a>')
        expected = xml('<a><x/><b>another</b><b>bar</b><b>baz</b><y/></a>')
        for new in ['another', ET.XML('<x>another</x>'), xml('<y>another</y>')]:
            ob.b = new
            self.assertEqual(expected, ob)

    def test_deletes_subelement(self):
        ob = xml('<a><b/></a>')
        del ob.b
        self.assertEqual(xml('<a/>'), ob)

    def test_raises_if_subelem_not_found(self):
        ob = xml('<a><b/></a>')
        with self.assertRaises(AttributeError):
            del ob.c

    def test_deletes_subelems_one_by_one(self):
        ob = xml('<a><b>foo</b><b>bar</b><b>baz</b></a>')
        del ob.b
        self.assertEqual(xml('<a><b>bar</b><b>baz</b></a>'), ob)
        del ob.b
        self.assertEqual(xml('<a><b>baz</b></a>'), ob)
        del ob.b
        self.assertEqual(xml('<a/>'), ob)
        with self.assertRaises(AttributeError):
            del ob.b


class TestModifyingSubelementsCornerCases(unittest.TestCase):

    def test_direct_access_to_instance_dict(self):
        ob = xml('<a/>')
        ob.__dict__['b'] = 'foo'
        self.assertEqual(xml('<a/>'), ob)
        self.assertEqual('foo', ob.b)

    def test_works_with_c_element_tree(self):
        import xml.etree.cElementTree as cET
        ob = etobj.objectify(cET.XML('<a/>'))
        ob.b = 'foo'
        self.assertEqual(xml('<a><b>foo</b></a>'), ob)

    def test_no_subelem_created_for_known_instance_properties(self):
        ob = xml('<a/>')
        ob.tag = 'b'
        ob.text = 'foo'
        ob.attrib['bar'] = 'baz'
        p = xml('<p/>')
        ob._parent = p
        self.assertIs(p, ob._parent)
        self.assertEqual(xml('<b bar="baz">foo</b>'), ob)

    def test_no_subelem_created_for_known_class_properties(self):
        ob = xml('<a/>')
        def foo():
            return 'foo'
        ob.keys = foo
        self.assertEqual('foo', ob.keys())
        self.assertEqual(xml('<a/>'), ob)

    def test_no_unnecessary_subelem_created_for_sublasses(self):
        class Foo(etobj.Element):
            def sayhello(self):
                return 'hello'
        ob = Foo(ET.XML('<a/>'))
        self.assertEqual('hello', ob.sayhello())

        def sayhi():
            return 'hi'
        ob.sayhello = sayhi

        def foo():
            return 'foo'
        ob.keys = foo

        ob.text = 'welcome'
        ob.b = 'bar'

        self.assertEqual('hi', ob.sayhello())
        self.assertEqual('foo', ob.keys())
        self.assertEqual(xml('<a>welcome<b>bar</b></a>'), ob)

    def test_deletes_regular_attributes_normally(self):
        ob = xml('<a/>')
        self.assertTrue(hasattr(ob, '_parent'))
        del ob._parent
        self.assertFalse(hasattr(ob, '_parent'))

    def test_forbids_deletion_of_properties(self):
        ob = xml('<a/>')
        for prop in ['tag', 'attrib', 'text', 'tail']:
            with self.assertRaises(AttributeError):
                delattr(ob, prop)


class TestSequenceLikeBehavior(unittest.TestCase):

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


class TestElemProperties(unittest.TestCase):

    def test_root_attr(self):
        ob = xml('<a n="zzz"><b/></a>')
        self.assertEqual('zzz', ob.get('n'))

    def test_root_text(self):
        ob = xml('<a>abc<b/>def</a>')
        self.assertEqual('abc', ob.text)

    def test_root_str(self):
        ob = xml('<a>abc<b/>def</a>')
        self.assertEqual('abc', str(ob))

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

    def test_subelem_tail(self):
        ob = xml('<a>xyz<b>abc</b>def</a>')
        self.assertEqual('def', ob.b.tail)

    def test_subelem_no_tail(self):
        ob = xml('<a><b>abc</b></a>')
        self.assertIsNone(ob.b.tail)

    def test_attrib(self):
        ob = xml('<a m="yyy" n="zzz"></a>')
        self.assertEqual(dict(m='yyy', n='zzz'), ob.attrib)

    def test_elem_property(self):
        ob = xml('<a foo="bar">baz</a>')
        self.assertEqual('a', ob.elem.tag)
        self.assertEqual(dict(foo='bar'), ob.elem.attrib)
        self.assertEqual('baz', ob.elem.text)

    def test_parent_property(self):
        ob = xml('<a><b><c/></b></a>')
        self.assertIsNone(ob.parent)
        self.assertEqual('a', ob.b.parent.tag)
        self.assertEqual('b', ob.b.c.parent.tag)
        self.assertEqual('a', ob.b.c.parent.parent.tag)


class TestComparison(unittest.TestCase):

    def test_root_eq_str(self):
        ob = xml('<a>abc<b/>def</a>')
        self.assertEqual(ob, 'abc')
        self.assertEqual('abc', ob)

    def test_root_ne_str(self):
        ob = xml('<a>abc<b/>def</a>')
        self.assertNotEqual(ob, 'xyz')
        self.assertNotEqual('xyz', ob)

    def test_root_eq_self(self):
        ob = xml('<a>abc<b/>def</a>')
        self.assertEqual(ob, ob)

    def test_elems_equal_if_same_content(self):
        ob1 = xml('<a m="bar" n="foo">abc<b/>def<c p="q">baz</c></a>')
        ob2 = xml('<a n="foo" m="bar">abc<b/>def<c p="q">baz</c></a>')
        self.assertEqual(ob1, ob2)

    def test_elems_not_equal_if_different_content(self):
        ob1 = xml('<a>abc</a>')
        ob2 = xml('<a n="foo">abc</a>')
        self.assertNotEqual(ob1, ob2)

    def test_elems_not_equal_if_extra_child(self):
        ob1 = xml('<a>abc<b/></a>')
        ob2 = xml('<a>abc</a>')
        self.assertNotEqual(ob1, ob2)

    def test_elems_not_equal_if_different_children(self):
        ob1 = xml('<a>abc<b/>foo</a>')
        ob2 = xml('<a>abc<b/>bar</a>')
        self.assertNotEqual(ob1, ob2)

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


class TestNamespaces(unittest.TestCase):

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


class TestUtilityFunctions(unittest.TestCase):

    def test_empty_shallow_signature(self):
        ob = etobj.Element(ET.Element('foo'))
        self.assertEqual(('foo', {}, None, [], None),
                         etobj.shallow_signature(ob))

    def test_shallow_signature(self):
        ob = xml('<a>xyz<b n="bar">abc</b>def</a>')
        self.assertEqual(('b', {'n':'bar'}, 'abc', [], 'def'),
                         etobj.shallow_signature(ob.b))

    def test_empty_deep_signature(self):
        ob = etobj.Element(ET.Element('foo'))
        self.assertEqual(('foo', {}, None, [], None), etobj.deep_signature(ob))

    def test_deep_signature(self):
        ob = xml('<a><b n="bar">abc<c m="foo">bar</c></b>def</a>')
        expected = ('b', {'n':'bar'}, 'abc',
                    [('c', {'m':'foo'}, 'bar', [], None)], 'def')
        self.assertEqual(expected, etobj.deep_signature(ob.b))

    def test_root(self):
        ob = xml('<a><b><c><d/></c></b></a>')
        for x in [ob, ob.b, ob.b.c, ob.b.c.d]:
            self.assertIs(ob, etobj.root(x))

    def test_iterancestors(self):
        ob = xml('<a><b><c><d/></c></b></a>')
        ancestors = list(etobj.iterancestors(ob.b.c.d))
        self.assertEqual(['c', 'b', 'a'], [a.tag for a in ancestors])
        self.assertEqual([], list(etobj.iterancestors(ob)))
