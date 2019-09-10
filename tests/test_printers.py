import unittest

from substra.cli.printers import find_dict_composite_key_value, get_leaderboard_printer, \
    get_asset_printer, JsonPrinter, YamlPrinter, LeaderBoardPrinter, AssetPrinter


class TestHelperMethods(unittest.TestCase):

    def test_find_dict_composite_key_value(self):
        self.assertIsNone(find_dict_composite_key_value({}, 'a'))
        self.assertIsNone(find_dict_composite_key_value({}, 'a.b'))
        self.assertIsNone(find_dict_composite_key_value({'a': None}, 'a.b'))
        with self.assertRaises(AttributeError):
            self.assertIsNone(find_dict_composite_key_value({'a': 'b'}, 'a.b'))

        self.assertEqual(find_dict_composite_key_value({'a': 'a'}, 'a'), 'a')
        self.assertEqual(find_dict_composite_key_value({'a': {'b': 'b'}}, 'a.b'), 'b')

    def test_get_asset_printer(self):
        self.assertIsInstance(get_asset_printer('algo', 'pretty'), AssetPrinter)
        self.assertIsInstance(get_asset_printer('algo', 'json'), JsonPrinter)
        self.assertIsInstance(get_asset_printer('algo', 'yaml'), YamlPrinter)

        self.assertIsInstance(get_asset_printer('foo', 'pretty'), JsonPrinter)
        self.assertIsInstance(get_asset_printer('foo', 'json'), JsonPrinter)
        self.assertIsInstance(get_asset_printer('foo', 'yaml'), YamlPrinter)

    def test_get_leaderboard_printer(self):
        self.assertIsInstance(get_leaderboard_printer('json'), JsonPrinter)
        self.assertIsInstance(get_leaderboard_printer('yaml'), YamlPrinter)
        self.assertIsInstance(get_leaderboard_printer('pretty'), LeaderBoardPrinter)
        self.assertIsInstance(get_leaderboard_printer('foo'), JsonPrinter)
