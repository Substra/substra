import unittest

from substra.cli.parsers import find_dict_composite_key_value


class TestHelperMethods(unittest.TestCase):

    def test_find_dict_composite_key_value(self):
        self.assertIsNone(find_dict_composite_key_value({}, 'a'))
        self.assertIsNone(find_dict_composite_key_value({}, 'a.b'))
        self.assertIsNone(find_dict_composite_key_value({'a': None}, 'a.b'))
        with self.assertRaises(AttributeError):
            self.assertIsNone(find_dict_composite_key_value({'a': 'b'}, 'a.b'))

        self.assertEqual(find_dict_composite_key_value({'a': 'a'}, 'a'), 'a')
        self.assertEqual(find_dict_composite_key_value({'a': {'b': 'b'}}, 'a.b'), 'b')
