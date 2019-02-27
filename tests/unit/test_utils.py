import os
from unittest import TestCase

from substra.utils import load_json_from_args

UNIT_TESTS_DIR = os.path.dirname(__file__)


class TestUtils(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.valid_json = '{"a": "b"}'
        cls.invalid_json = '{a : b}'
        cls.invalid_args = 'non_existing_path.json'
        cls.path_to_valid_json = os.path.join(UNIT_TESTS_DIR, 'tmp_valid.json')
        cls.path_to_invalid_json = os.path.join(UNIT_TESTS_DIR, 'tmp_invalid.json')
        cls.invalid_path = ''

        with open(cls.path_to_valid_json, 'w') as f:
            f.write(cls.valid_json)
            f.close()

        with open(cls.path_to_invalid_json, 'w') as f:
            f.write(cls.invalid_json)
            f.close()

    def tearDown(self):
        os.remove(self.path_to_valid_json)
        os.remove(self.path_to_invalid_json)

    def test_load_json_from_args(self):
        # valid arguments
        self.assertEqual(load_json_from_args(self.valid_json), {"a": "b"})
        self.assertEqual(load_json_from_args(self.path_to_valid_json), {"a": "b"})

        # invalid arguments

        with self.assertRaises(Exception) as cm:
            load_json_from_args(self.invalid_json)
        self.assertTrue(str(cm.exception).startswith(f'String "{self.invalid_json}" is not valid JSON:'))

        with self.assertRaises(Exception) as cm:
            load_json_from_args(self.path_to_invalid_json)
        self.assertTrue(str(cm.exception).startswith(f'File "{self.path_to_invalid_json}" is not a valid JSON file:'))

        with self.assertRaises(Exception) as cm:
            load_json_from_args(self.invalid_args)
        self.assertTrue(str(cm.exception).startswith(f'String "{self.invalid_args}" is neither a path to a JSON file nor valid JSON:'))
