import unittest
from unittest.mock import Mock

from substra.cli.parsers import get_recursive, get_prop_value, handle_raw_option


class TestHelperMethods(unittest.TestCase):

    def test_get_recursive(self):
        self.assertIsNone(get_recursive({}, 'a'))
        self.assertIsNone(get_recursive({}, 'a.b'))
        self.assertIsNone(get_recursive({'a': None}, 'a.b'))
        with self.assertRaises(AttributeError):
            self.assertIsNone(get_recursive({'a': 'b'}, 'a.b'))

        self.assertEqual(get_recursive({'a': 'a'}, 'a'), 'a')
        self.assertEqual(get_recursive({'a': {'b': 'b'}}, 'a.b'), 'b')

    def test_get_prop_value(self):
        obj = {'a': {'b': 'c'}}
        self.assertEqual(get_prop_value(obj, 'a.b'), 'c')
        self.assertEqual(get_prop_value(obj, lambda x: x['a']['b']), 'c')

    def test_handle_raw_option(self):
        m = Mock()

        class Dummy:
            @handle_raw_option
            def dummy(self, data):
                m(data)

        dummy = Dummy()

        m.assert_not_called()
        dummy.dummy({'a': {'b': 'c'}}, True)
        m.assert_not_called()
        dummy.dummy({'a': {'b': 'c'}}, False)
        m.assert_called_with({'a': {'b': 'c'}})
