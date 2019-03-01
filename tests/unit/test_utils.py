import os
from unittest import TestCase
from unittest.mock import mock_open, patch

from substra.utils import load_json_from_args, InvalidJSONStringException, InvalidJSONFileException, \
    InvalidJSONArgsException

UNIT_TESTS_DIR = os.path.dirname(__file__)


class TestUtils(TestCase):

    def setUp(self):
        self.valid_json = '{"a": "b"}'
        self.invalid_json = 'non_existing_path.json'
        self.path_to_valid_json = 'tmp_valid.json'
        self.path_to_invalid_json = 'tmp_invalid.json'

    def test_load_json_valid_args(self):
        self.assertEqual(load_json_from_args(self.valid_json), {"a": "b"})

    @patch('os.path.isfile')
    def test_load_json_valid_path(self, mock_isfile):
        mock_isfile.return_value = True
        with patch('builtins.open',  mock_open(read_data=self.valid_json)) as mock_file:
            self.assertEqual(load_json_from_args(self.path_to_valid_json), {"a": "b"})
            mock_file.assert_called_with(self.path_to_valid_json, 'r')

    def test_load_json_invalid_args(self):
        # invalid arguments
        with self.assertRaises(InvalidJSONArgsException) as cm:
            load_json_from_args(self.invalid_json)

        self.assertTrue(type(cm.exception) != InvalidJSONStringException)
        self.assertTrue(type(cm.exception) != InvalidJSONFileException)

    def test_load_json_invalid_json(self):
        with self.assertRaises(InvalidJSONStringException):
            load_json_from_args('{a : b}')

    def test_load_json_invalid_json_bool(self):
        with self.assertRaises(InvalidJSONStringException):
            load_json_from_args('true')

    def test_load_json_invalid_json_int(self):
        with self.assertRaises(InvalidJSONStringException):
            load_json_from_args('1')

    def test_load_json_invalid_json_malformed(self):
        with self.assertRaises(InvalidJSONStringException):
            load_json_from_args('{,}')

    @patch('os.path.isfile')
    def test_load_json_path_to_invalid_json(self, mock_isfile):
        mock_isfile.return_value = True
        with self.assertRaises(InvalidJSONFileException):
            with patch('builtins.open', mock_open(read_data=self.invalid_json)) as mock_file:
                load_json_from_args(self.path_to_invalid_json)
                mock_file.assert_called_with(self.path_to_invalid_json, 'r')
